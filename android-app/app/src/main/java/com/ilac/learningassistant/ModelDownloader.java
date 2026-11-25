package com.ilac.learningassistant;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;

public class ModelDownloader {

    private static final String MODEL_URL =
        "https://huggingface.co/executorch-community/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8-ET/resolve/main/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte";

    private static final String TOKENIZER_URL =
        "https://huggingface.co/executorch-community/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8-ET/resolve/main/tokenizer.model";

    private static final String MODEL_SHA256 =
        "8715cdba9e91f6bede00cc5f2d6b12397b95225da5630c4972a8da03001cda3b";

    private static final Handler mainHandler =
        new Handler(Looper.getMainLooper());

    public interface Listener {
        void onProgress(String fileName, long downloaded, long total);
        void onComplete(File model, File tokenizer);
        void onError(String message);
    }

    public static void download(Context context, Listener listener) {

        new Thread(() -> {
            try {
                File folder = new File(context.getFilesDir(), "models");

                if (!folder.exists() && !folder.mkdirs()) {
                    throw new Exception("Cannot create model folder.");
                }

                File model = new File(folder,
                    "Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte");

                File tokenizer = new File(folder, "tokenizer.model");

                downloadFile(MODEL_URL, model, listener, true);
                downloadFile(TOKENIZER_URL, tokenizer, listener, false);

                mainHandler.post(() ->
                    listener.onComplete(model, tokenizer));

            } catch (Exception e) {
                mainHandler.post(() ->
                    listener.onError(e.getMessage()));
            }
        }).start();
    }

    private static void downloadFile(
        String urlString,
        File destination,
        Listener listener,
        boolean verifyHash
    ) throws Exception {

        File temporary = new File(destination.getAbsolutePath() + ".part");

        if (temporary.exists()) {
            temporary.delete();
        }

        HttpURLConnection connection =
            (HttpURLConnection) new URL(urlString).openConnection();

        connection.setConnectTimeout(30000);
        connection.setReadTimeout(120000);
        connection.setInstanceFollowRedirects(true);
        connection.connect();

        try {
            int response = connection.getResponseCode();

            if (response != HttpURLConnection.HTTP_OK) {
                throw new Exception("Download failed. HTTP " + response);
            }

            long total = connection.getContentLengthLong();

            MessageDigest digest = verifyHash
                ? MessageDigest.getInstance("SHA-256") : null;

            long downloaded = 0;
            byte[] buffer = new byte[1024 * 1024];

            try (InputStream input = connection.getInputStream();
                 FileOutputStream output = new FileOutputStream(temporary)) {

                int count;

                while ((count = input.read(buffer)) != -1) {
                    output.write(buffer, 0, count);

                    if (digest != null) {
                        digest.update(buffer, 0, count);
                    }

                    downloaded += count;

                    long current = downloaded;

                    mainHandler.post(() ->
                        listener.onProgress(
                            destination.getName(), current, total));
                }

                output.getFD().sync();
            }

            if (total > 0 && downloaded != total) {
                throw new Exception("Incomplete download. Please retry.");
            }

            if (downloaded == 0) {
                throw new Exception("Downloaded file is empty.");
            }

            if (verifyHash) {
                StringBuilder hash = new StringBuilder();

                for (byte b : digest.digest()) {
                    hash.append(String.format("%02x", b));
                }

                if (!MODEL_SHA256.equals(hash.toString())) {
                    throw new Exception("Model checksum verification failed.");
                }
            }

            if (destination.exists()) {
                destination.delete();
            }

            if (!temporary.renameTo(destination)) {
                throw new Exception("Could not save downloaded file.");
            }

        } finally {
            connection.disconnect();
        }
    }
}
