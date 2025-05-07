const taskId = "[[${taskId}]]";

console.log("taskId:", taskId);
if(taskId && taskId.trim() !== ""){
    const intervalId = setInterval(() => {
        fetch(`http://14.46.29.200:3500/progress?task_id=${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.current_page !== undefined && data.total_pages !== undefined) {
                    document.getElementById('progressText').innerText =
                        `현재 ${data.current_page}/${data.total_pages} 페이지 작업 중...`;

                    if (data.current_page === data.total_pages) {
                        clearInterval(intervalId);
                        document.getElementById('progressText').innerText = "분석 완료!";

                        // 분석 끝나면 결과 가져오기
                        fetch(`http://14.46.29.200:3500/result?task_id=${taskId}`)
                            .then(response => response.json())
                            .then(resultData => {
                                console.log("최종 요약 결과:", resultData);

                                // 결과를 웹에 표시
                                const resultDiv = document.createElement("div");
                                resultDiv.innerHTML = "<h3>요약 결과</h3><pre>" + JSON.stringify(resultData, null, 2) + "</pre>";
                                document.body.appendChild(resultDiv);
                            })
                            .catch(error => {
                                console.error("요약 결과 요청 오류:", error);
                            });
                    }
                }
            })
            .catch(error => {
                console.error("Progress 요청 중 오류:", error);
            });
    }, 2000);
}