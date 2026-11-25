
package com.ilac.learningassistant;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;

import org.pytorch.executorch.extension.llm.LlmModule;
import org.pytorch.executorch.extension.llm.LlmCallback;
import org.pytorch.executorch.extension.llm.LlmGenerationConfig;

import java.io.File;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LocalAI {

    public interface Listener {
        void onLoaded();
        void onProgress(String response);
        void onResponse(String response);
        void onError(String error);
    }

    private LlmModule module;
    private volatile boolean loaded = false;

    private final Handler mainHandler =
            new Handler(Looper.getMainLooper());

    private final ExecutorService executor =
            Executors.newSingleThreadExecutor();

    public void load(Context context, Listener listener) {

        executor.execute(() -> {
            try {
                File folder = new File(
                        context.getFilesDir(), "models");

                File model = new File(folder,
                        "Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte");

                File tokenizer = new File(folder,
                        "tokenizer.model");

                if (!model.exists() || !tokenizer.exists()) {
                    throw new Exception(
                            "Model or tokenizer file not found.");
                }

                module = new LlmModule(
                        model.getAbsolutePath(),
                        tokenizer.getAbsolutePath(),
                        0.7f
                );

                module.load();
                loaded = true;

                mainHandler.post(listener::onLoaded);

            } catch (Exception e) {
                mainHandler.post(() ->
                        listener.onError(String.valueOf(e.getMessage())));
            }
        });
    }

    public void ask(String question, Listener listener) {

        executor.execute(() -> {
            try {
                if (!loaded || module == null) {
                    throw new Exception("AI model is not loaded.");
                }

                String prompt =
                         "You are ILAC (Intelligent Learning Assistant Chip), "
        + "an academic learning assistant for engineering students. "
        + "Your purpose is to teach concepts, not to have casual conversations. "
        + "Give accurate, structured, educational answers. "
        + "Use this format for academic questions:\n"
        + "1. Definition\n"
        + "2. Working Principle\n"
        + "3. Important Points\n"
        + "4. Simple Example\n"
        + "5. Short Summary\n"
        + "Use simple language and explain technical terms. "
        + "Avoid unnecessary greetings and conversational filler. "
        + "If the question is not academic, politely guide the student "
        + "back to learning.\n"
        + "Student Question: " + question
        + "\nILAC Educational Answer:";

                StringBuilder response = new StringBuilder();

                LlmGenerationConfig config =
                        LlmGenerationConfig.create()
                                .maxNewTokens(128)
                                .temperature(0.7f)
                                .build();

                module.generate(prompt, config, new LlmCallback() {

                    @Override
                    public void onResult(String token) {
                        response.append(token);

                        String current = response.toString();

                        mainHandler.post(() ->
                                listener.onProgress(current));
                    }

                    @Override
                    public void onStats(String statsJson) {
                        String answer = response.toString().trim();

                        mainHandler.post(() ->
                                listener.onResponse(answer));
                    }

                    @Override
                    public void onError(int errorCode, String message) {
                        mainHandler.post(() ->
                                listener.onError(
                                        "Error " + errorCode + ": " + message));
                    }
                });

            } catch (Exception e) {
                mainHandler.post(() ->
                        listener.onError(String.valueOf(e.getMessage())));
            }
        });
    }

    public void close() {
        executor.execute(() -> {
            if (module != null) {
                module.stop();
                module.close();
                module = null;
                loaded = false;
            }
        });

        executor.shutdown();
    }
}
