      const API_URL = "/generate-questions";

      const form = document.getElementById("jobForm");
      const jobTitleInput = document.getElementById("jobTitle");
      const submitBtn = document.getElementById("submitBtn");

      const inlineError = document.getElementById("inlineError");
      const loaderRow = document.getElementById("loaderRow");

      const results = document.getElementById("results");
      const questionsList = document.getElementById("questionsList");

      function setLoading(isLoading) {
        submitBtn.disabled = isLoading;
        loaderRow.classList.toggle("show", isLoading);
      }

      function resetUI() {
        inlineError.textContent = "";
        questionsList.innerHTML = "";
        results.classList.remove("show");
      }

      function renderQuestions(questions) {
        questionsList.innerHTML = "";

        questions.forEach((q, i) => {
          const li = document.createElement("li");
          li.className = "question";

          const bubble = document.createElement("div");
          bubble.className = "idx";
          bubble.textContent = String(i + 1);

          const textWrap = document.createElement("div");
          textWrap.style.display = "flex";
          textWrap.style.alignItems = "flex-start";

          textWrap.appendChild(bubble);

          const span = document.createElement("span");
          span.textContent = String(q);
          textWrap.appendChild(span);

          li.appendChild(textWrap);
          questionsList.appendChild(li);
        });

        results.classList.add("show");
      }

      async function handleSubmit(event) {
        event.preventDefault();

        resetUI();

        const jobTitle = jobTitleInput.value.trim();
        if (!jobTitle) {
          inlineError.textContent = "Job Title is required.";
          return;
        }

        setLoading(true);

        try {
          const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ job_title: jobTitle }),
          });

          const data = await response.json().catch(() => null);

          if (!response.ok) {
            inlineError.textContent =
              data && data.error ? data.error : "Failed to generate questions.";
            return;
          }

          const questions = data && Array.isArray(data.questions) ? data.questions : null;
          if (!questions || questions.length !== 3) {
            inlineError.textContent = "Unexpected response format from backend.";
            return;
          }

          renderQuestions(questions);
        } catch (err) {
          inlineError.textContent =
            "Network error: could not reach the backend. Start Flask and try again.";
        } finally {
          setLoading(false);
        }
      }

      form.addEventListener("submit", handleSubmit);