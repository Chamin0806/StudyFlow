document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const taskId = params.get("taskId");

    if (!taskId || taskId.trim() === "") return;

    const loader = document.getElementById("loader");
    const progressText = document.getElementById("progressText");
    const resultBox = document.getElementById("result-box");

    const intervalId = setInterval(() => {
        fetch(`http://localhost:3500/progress?task_id=${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.current_page !== undefined && data.total_pages !== undefined) {
                    const percent = Math.floor((data.current_page / data.total_pages) * 100);
                    loader.value = percent;
                    progressText.innerText =
                        `현재 ${data.current_page}/${data.total_pages} 페이지 작업 중... (${percent}%)`;

                    if (data.done === true) {
                        clearInterval(intervalId);
                        progressText.innerText = "✅ 분석 완료! 곧 결과 페이지로 이동됩니다.";

                        setTimeout(() => {
                            fetch(`http://localhost:3500/result?task_id=${taskId}`)
                                .then(res => res.json())
                                .then(json => {
                                    loader.style.display = "none";
                                    progressText.style.display = "none";

                                    const pre = document.createElement("pre");
                                    pre.textContent = JSON.stringify(json, null, 2);
                                    pre.style.fontFamily = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";
                                    pre.style.fontSize = "16px";
                                    pre.style.lineHeight = "1.6";
                                    pre.style.whiteSpace = "pre-wrap";
                                    pre.style.wordWrap = "break-word";
                                    pre.style.overflowWrap = "break-word";
                                    pre.style.margin = "0";

                                    resultBox.innerHTML = "<h3>🔥 요약 결과 🔥</h3>";
                                    resultBox.appendChild(pre);
                                })
                                .catch(err => {
                                    loader.style.display = "none";
                                    progressText.style.display = "none";
                                    resultBox.innerHTML = "<p style='color:red;'>결과 요청 실패</p>";
                                    console.error("결과 요청 오류:", err);
                                });
                        }, 1000);



                    }
                }
            })
            .catch(err => {
                console.error("진행 상황 요청 오류:", err);
            });
    }, 2000);
});

function scrollToForm() {
    const formElement = document.getElementById("uploadForm");
    if (formElement) {
        const elementTop = formElement.getBoundingClientRect().top;
        const offset = window.scrollY + elementTop - (window.innerHeight / 2) + (formElement.offsetHeight / 2);

        window.scrollTo({
            top: offset,
            behavior: "smooth"
        });
    }
}

function handleSubmit(event) {
    event.preventDefault();

    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    const file = formData.get("file");
    const startPage = formData.get("startPage");
    const endPage = formData.get("endPage");
    const options = formData.getAll("options");

    const hasRecommendation = options.includes("recommendation");
    const hasQuestion = options.includes("question");

    const uploadUrl = "/upload";
    const xhr = new XMLHttpRequest();
    xhr.open("POST", uploadUrl);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200 || xhr.status === 302) {
                window.location.href = xhr.responseURL;
            } else {
                alert("파일 업로드에 실패했습니다.");
            }
        }
    };

    const finalForm = new FormData();
    finalForm.append("file", file);
    finalForm.append("startPage", startPage);
    finalForm.append("endPage", endPage);
    if (hasRecommendation) finalForm.append("options", "recommend");
    if (hasQuestion) finalForm.append("options", "question");

    xhr.send(finalForm);
}
document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="options"]');
    const summaryBox = document.getElementById('selected-options-summary');
    const selectedList = document.getElementById('selected-list');

    if (!checkboxes.length || !summaryBox || !selectedList) {
        return; // 요소가 없으면 아무 것도 하지 않음 (오류 방지용)
    }

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => {
            const selected = Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.nextElementSibling.textContent);

            if (selected.length > 0) {
                summaryBox.style.display = 'block';
                selectedList.textContent = selected.join(', ');
            } else {
                summaryBox.style.display = 'none';
                selectedList.textContent = '';
            }
        });
    });
});

//사용자가 업로드한 pdf 표시
document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector('input[type="file"]');
    const fileNameDisplay = document.getElementById("file-name");

    if (!fileInput || !fileNameDisplay) return;

    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (file) {
            fileNameDisplay.textContent = `선택된 파일: ${file.name}`;
            fileNameDisplay.style.display = "block";
        } else {
            fileNameDisplay.textContent = "";
            fileNameDisplay.style.display = "none";
        }
    });
});
