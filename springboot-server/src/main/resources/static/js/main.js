document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const taskId = params.get("taskId");

    if (!taskId || taskId.trim() === "") {
        return;
    }

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

                    if (data.current_page === data.total_pages) {
                        clearInterval(intervalId);
                        progressText.innerText = "✅ 분석 완료! 곧 결과 페이지로 이동됩니다.";


                        // result 요청 약간 지연 (파이썬에서 결과를 저장하기 전에 요청해서 오류나는 경우가 있었음)
                        setTimeout(() => {
                            fetch(`http://localhost:3500/result?task_id=${taskId}`)
                                .then(res => res.json())
                                .then(json => {
                                    loader.style.display = "none";
                                    progressText.style.display = "none";
                                    const pre = document.createElement("pre");
                                    pre.textContent = JSON.stringify(json, null, 2);
                                    resultBox.innerHTML = "<h3>요약 결과</h3>";
                                    resultBox.appendChild(pre);
                                })
                                .catch(err => {
                                    loader.style.display = "none";
                                    progressText.style.display = "none";
                                    resultBox.innerHTML = "<p style='color:red;'>결과 요청 실패</p>";
                                    console.error("결과 요청 오류:", err);
                                });
                        }, 1000); // 1초 딜레이
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
