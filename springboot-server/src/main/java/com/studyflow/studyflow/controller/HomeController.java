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
            // 1. 저장할 절대 경로 지정 (현재 프로젝트 기준)
            String uploadDir = System.getProperty("user.dir") + "/uploads/";

            File directory = new File(uploadDir);
            if (!directory.exists()) {
                directory.mkdirs();
            }

            // 2. 파일 이름 중복 방지 (시간+이름 조합)
            String fileName = System.currentTimeMillis() + "_" + file.getOriginalFilename();
            String filePath = uploadDir + fileName;

            file.transferTo(new File(filePath));

            model.addAttribute("message", "파일 업로드 성공: " + fileName);

        } catch (IOException e) {
            e.printStackTrace();
            model.addAttribute("message", "파일 업로드 실패: " + e.getMessage());
        }

        return "index";
    }

}