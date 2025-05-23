package com.studyflow.studyflow.controller;

import com.studyflow.studyflow.service.PythonAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.io.File;
import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;

@Controller
@RequiredArgsConstructor //Lombok에서 final로 생성된 필드를 자동으로 생성자에 넣어줌. 생성자 주입으로 받고싶을 때 사용
public class HomeController {
    private final PythonAnalysisService pythonService;

    @GetMapping("/")
    public String home() {
        return "index";
    }

    @PostMapping("/upload")
    public String handleFileUpload(@RequestParam("file") MultipartFile file,
                                   @RequestParam("startPage") int startPage,
                                   @RequestParam("endPage") int endPage,
                                   @RequestParam(value = "options", required = false) List<String> options,
                                   RedirectAttributes redirectAttributes) {
        if (file.isEmpty()) {
            redirectAttributes.addFlashAttribute("message", "파일을 선택하지 않았습니다.");
            return "redirect:/";
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

            boolean needRecommendation = options != null && options.contains("recommend");
            boolean needQuestion = options != null && options.contains("question");

            String pythonServerUrl = String.format(
                    "http://14.46.29.200:3500/process?filename=%s&start_page=%d&end_page=%d&recommend=%b&question=%b",
                    URLEncoder.encode(fileName, StandardCharsets.UTF_8),
                    startPage,
                    endPage,
                    needRecommendation,
                    needQuestion
            );

            String taskId = pythonService.requestTaskIdFromPython(pythonServerUrl);

            if (taskId != null && !taskId.isBlank()) {
                return "redirect:/result?taskId=" + taskId;
            } else {
                redirectAttributes.addFlashAttribute("message", "처리 실패: taskId를 받을 수 없습니다.");
                return "redirect:/";
            }

        } catch (IOException e) {
            e.printStackTrace();
            redirectAttributes.addFlashAttribute("message", "파일 업로드 실패: " + e.getMessage());
            return "redirect:/";
        }
    }

    @GetMapping("/result")
    public String resultPage(@RequestParam("taskId") String taskId, Model model) {
        model.addAttribute("taskId", taskId);  // thymeLeaf에다가 넘겨줌 index.html에서 {taskId} 이런식으로 사용가능함
        return "index";
    }
}
