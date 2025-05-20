package com.studyflow.studyflow.service;

import org.springframework.stereotype.Service;

import javax.print.DocFlavor;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

@Service
public class PythonAnalysisService {

    public String requestTaskIdFromPython(String url) {
        try {
            URL pythonUrl = new URL(url);
            HttpURLConnection connection = (HttpURLConnection) pythonUrl.openConnection();
            connection.setRequestMethod("GET");

            Scanner scanner = new Scanner(connection.getInputStream());
            String response = scanner.useDelimiter("\\A").next();
            scanner.close();
            connection.disconnect();

            int idx = response.indexOf("task_id");
            if (idx != -1) {
                int start = response.indexOf(":", idx) + 2;
                int end = response.indexOf("\"", start);
                return response.substring(start, end);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }
}

