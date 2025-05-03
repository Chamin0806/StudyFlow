package com.studyflow.studyflow.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;

@Controller
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "index"; // src/main/resources/templates/index.html 렌더링
    }

    @PostMapping("/upload")
    public String handleFileUpload(@RequestParam("file") MultipartFile file, Model model) {
        if (file.isEmpty()) {
            model.addAttribute("message", "파일을 선택하지 않았습니다.");
            return "index";
        }

        try {
            // 저장할 폴더 경로
            String uploadDir = "uploads/";
            File directory = new File(uploadDir);
            if (!directory.exists()) {
                directory.mkdirs(); // 없으면 폴더 생성
            }

            // 파일 저장
            String filePath = uploadDir + file.getOriginalFilename();
            file.transferTo(new File(filePath));

            model.addAttribute("message", "파일 업로드 성공: " + file.getOriginalFilename());

        } catch (IOException e) {
            e.printStackTrace();
            model.addAttribute("message", "파일 업로드 실패: " + e.getMessage());
        }

        return "index"; // 업로드 후 다시 index.html로
    }
}