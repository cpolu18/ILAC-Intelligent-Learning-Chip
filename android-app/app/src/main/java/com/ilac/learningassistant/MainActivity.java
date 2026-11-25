
package com.ilac.learningassistant;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.ProgressBar;

public class MainActivity extends Activity {

    LinearLayout chatLayout;
    ScrollView scrollView;
    EditText questionInput;

    Button downloadButton;
    Button loadButton;
    Button sendButton;

    ProgressBar progressBar;
    TextView downloadStatus;

    LocalAI ai = new LocalAI();

    boolean modelLoaded = false;
    int padding = 16;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(padding, padding, padding, padding);
        root.setBackgroundColor(Color.rgb(245, 247, 250));

        TextView title = new TextView(this);
        title.setText("ILAC Learning Assistant");
        title.setTextSize(24);
        title.setTypeface(null, Typeface.BOLD);
        title.setTextColor(Color.rgb(25, 55, 95));
        title.setGravity(Gravity.CENTER);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("Your personal learning companion");
        subtitle.setTextSize(14);
        subtitle.setTextColor(Color.DKGRAY);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 6, 0, 18);
        root.addView(subtitle);

        TextView subjects = new TextView(this);
        subjects.setText(
                "Electronics  |  VLSI  |  Mathematics  |  Programming");
        subjects.setTextSize(12);
        subjects.setTextColor(Color.rgb(35, 90, 150));
        subjects.setGravity(Gravity.CENTER);
        subjects.setPadding(4, 12, 4, 12);
        root.addView(subjects);

        // MODEL DOWNLOAD

        downloadButton = new Button(this);
        downloadButton.setText("Download AI Model");

        downloadStatus = new TextView(this);
        downloadStatus.setText("AI model download verified previously.");
        downloadStatus.setTextSize(12);
        downloadStatus.setPadding(4, 4, 4, 4);

        progressBar = new ProgressBar(
                this, null,
                android.R.attr.progressBarStyleHorizontal);

        progressBar.setMax(100);
        progressBar.setVisibility(View.GONE);

        root.addView(downloadButton);
        root.addView(downloadStatus);
        root.addView(progressBar);

        // LOAD MODEL

        loadButton = new Button(this);
        loadButton.setText("Load AI Model");
        root.addView(loadButton);

        loadButton.setOnClickListener(v -> {

            loadButton.setEnabled(false);
            downloadStatus.setText(
                    "Loading AI model into memory. Please wait...");

            ai.load(this, new LocalAI.Listener() {

                @Override
                public void onLoaded() {
                    modelLoaded = true;

                    downloadStatus.setText(
                            "ILAC AI model loaded successfully. Ready to chat.");

                    loadButton.setText("AI Model Loaded");
                }

                @Override
                public void onResponse(String response) {
                }

                @Override
                public void onError(String error) {
                    modelLoaded = false;

                    downloadStatus.setText(
                            "Model loading failed: " + error);

                    loadButton.setText("Retry Load");
                    loadButton.setEnabled(true);
                }
            });
        });

        // CHAT

        scrollView = new ScrollView(this);

        chatLayout = new LinearLayout(this);
        chatLayout.setOrientation(LinearLayout.VERTICAL);
        chatLayout.setPadding(4, 12, 4, 12);

        scrollView.addView(chatLayout);

        LinearLayout.LayoutParams chatParams =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        0,
                        1);

        root.addView(scrollView, chatParams);

        addMessage(
                "ILAC",
                "Hello! Welcome to ILAC. Load the AI model and ask me a question."
        );

        // INPUT

        LinearLayout inputRow = new LinearLayout(this);
        inputRow.setOrientation(LinearLayout.HORIZONTAL);
        inputRow.setGravity(Gravity.CENTER_VERTICAL);

        questionInput = new EditText(this);
        questionInput.setHint("Ask your question...");
        questionInput.setTextSize(15);
        questionInput.setMinHeight(52);
        questionInput.setPadding(12, 8, 12, 8);

        LinearLayout.LayoutParams inputParams =
                new LinearLayout.LayoutParams(
                        0,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        1);

        inputRow.addView(questionInput, inputParams);

        sendButton = new Button(this);
        sendButton.setText("Send");

        inputRow.addView(sendButton);
        root.addView(inputRow);

        sendButton.setOnClickListener(v -> sendMessage());

        // DOWNLOAD BUTTON

        downloadButton.setOnClickListener(v -> {

            downloadButton.setEnabled(false);
            downloadStatus.setText("Starting model download...");
            progressBar.setVisibility(View.VISIBLE);
            progressBar.setProgress(0);

            ModelDownloader.download(
                    this,
                    new ModelDownloader.Listener() {

                @Override
                public void onProgress(
                        String fileName, long current, long total) {

                    if (total > 0) {
                        int percent =
                                (int) ((current * 100) / total);

                        progressBar.setProgress(percent);

                        downloadStatus.setText(
                                "Downloading " + fileName +
                                ": " + percent + "%");
                    }
                }

                @Override
                public void onComplete(
                        java.io.File model,
                        java.io.File tokenizer) {

                    progressBar.setProgress(100);

                    downloadStatus.setText(
                            "Model and tokenizer downloaded and verified.");

                    downloadButton.setText("Model Downloaded");
                    downloadButton.setEnabled(false);

                    loadButton.setEnabled(true);
                }

                @Override
                public void onError(String message) {

                    downloadStatus.setText(
                            "Download failed: " + message);

                    downloadButton.setText("Retry Download");
                    downloadButton.setEnabled(true);
                }
            });
        });

        setContentView(root);
    }

    private void sendMessage() {

        String question =
                questionInput.getText().toString().trim();

        if (question.isEmpty()) {
            return;
        }

        if (!modelLoaded) {
            addMessage(
                    "ILAC",
                    "Please load the AI model before asking questions."
            );
            return;
        }

        addMessage("You", question);
        questionInput.setText("");

        sendButton.setEnabled(false);

        addMessage("ILAC", "Generating response...");

        ai.ask(question, new LocalAI.Listener() {

            @Override
            public void onLoaded() {
            }

            @Override
            public void onResponse(String response) {

                sendButton.setEnabled(true);

                if (response.isEmpty()) {
                    addMessage(
                            "ILAC",
                            "The model returned an empty response.");
                } else {
                    addMessage("ILAC", response);
                }
            }

            @Override
            public void onError(String error) {

                sendButton.setEnabled(true);

                addMessage(
                        "ILAC",
                        "AI inference error: " + error);
            }
        });
    }

    private void addMessage(String sender, String message) {

        TextView text = new TextView(this);

        text.setText(sender + "\n" + message);
        text.setTextSize(15);
        text.setTextColor(Color.rgb(35, 45, 60));
        text.setPadding(16, 14, 16, 14);

        text.setBackgroundColor(
                sender.equals("You")
                        ? Color.rgb(220, 235, 255)
                        : Color.WHITE
        );

        LinearLayout.LayoutParams params =
                new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT);

        params.setMargins(0, 6, 0, 6);

        chatLayout.addView(text, params);

        scrollView.post(
                () -> scrollView.fullScroll(View.FOCUS_DOWN));
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        ai.close();
    }
}
