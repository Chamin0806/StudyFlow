package com.studyflow.studyflow.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

@Controller
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "index";  // templates/index.html
    }

    @PostMapping("/upload")
    public String handleFileUpload(@RequestParam("file") MultipartFile file,
                                   @RequestParam("startPage") int startPage,
                                   @RequestParam("endPage") int endPage,
                                   Model model) {
        if (file.isEmpty()) {
            model.addAttribute("message", "파일을 선택하지 않았습니다.");
            return "index";
        }

        try {
            String uploadDir = System.getProperty("user.dir") + "/uploads/";
            File directory = new File(uploadDir);
            if (!directory.exists()) {
                directory.mkdirs();
            }

            String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
            String filePath = uploadDir + fileName;
            file.transferTo(new File(filePath));

            String pythonServerUrl = "http://14.46.29.200:3500/process?filename=" + fileName +
                    "&start_page=" + startPage +
                    "&end_page=" + endPage;

            String taskId = sendRequestToPythonServer(pythonServerUrl);

            model.addAttribute("message", "파일 업로드 및 처리 요청 완료");
            model.addAttribute("taskId", taskId);
            model.addAttribute("filename", fileName);

        } catch (IOException e) {
            e.printStackTrace();
            model.addAttribute("message", "파일 업로드 실패: " + e.getMessage());
        }

        return "index";
    }

    private String sendRequestToPythonServer(String url) {
        try {
            URL pythonUrl = new URL(url);
            HttpURLConnection connection = (HttpURLConnection) pythonUrl.openConnection();
            connection.setRequestMethod("GET");

            Scanner scanner = new Scanner(connection.getInputStream());
            String response = scanner.useDelimiter("\\A").next();
            scanner.close();
            connection.disconnect();

            // 응답 JSON에서 task_id 추출
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
