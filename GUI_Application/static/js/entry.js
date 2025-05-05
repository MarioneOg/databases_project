const buttons = document.querySelectorAll('.entry-button');

const projectForm = document.getElementById('project-form');
const postForm = document.getElementById('post-form');
const analysisForm = document.getElementById('analysis-form');

// Toggle visibility of text fields and selection
buttons.forEach(button => {
    button.addEventListener('click', () => {
        const isSelected = button.classList.contains('selected');

        buttons.forEach(btn => btn.classList.remove('selected'));
        projectForm.classList.add('hidden');
        postForm.classList.add('hidden');
        analysisForm.classList.add('hidden');

        if (!isSelected) {
            button.classList.add('selected');

            if (button.id === 'project-btn') {
                projectForm.classList.remove('hidden');
            } else if (button.id === 'posts-btn') {
                postForm.classList.remove('hidden');
            } else if (button.id === 'analysis-btn') {
                analysisForm.classList.remove('hidden');
            }
        }
    });
});

// Add project parameters
document.getElementById("submit-project").addEventListener("click", () => {
    const projectData = {
        projectName: document.getElementById("project-name").value.trim(),
        managerFirst: document.getElementById("project-manager-fn").value.trim(),
        managerLast: document.getElementById("project-manager-ln").value.trim(),
        institute: document.getElementById("institute-name").value.trim(),
        startDate: document.getElementById("start-date").value.trim(),
        endDate: document.getElementById("end-date").value.trim()
    };

    console.log("Project submission:", projectData);
    // Backend connection goes here???
});

// Add post parameters
document.getElementById("submit-post").addEventListener("click", () => {
    event.preventDefault(); 
    const ageValue = document.getElementById("age").value.trim();

    if (isNaN(ageValue) || Number(ageValue) < 0) {
        alert("Age must be a non-negative number.");
        return; // Stop form submission
    }

    const postData = {
        projectName: document.getElementById("post-project-name").value.trim(),
        userInfo: {
            username: document.getElementById("username").value.trim(),
            socialMedia: document.getElementById("social-media").value.trim(),
            firstName: document.getElementById("user-first-name").value.trim(),
            lastName: document.getElementById("user-last-name").value.trim(),
            birthCountry: document.getElementById("birth-country").value.trim(),
            residenceCountry: document.getElementById("residence-country").value.trim(),
            age: document.getElementById("age").value.trim(),
            gender: document.getElementById("gender").value.trim(),
            verified: document.getElementById("verified").value.trim()
        },
        originalPost: {
            time: document.getElementById("post-time").value.trim(),
            text: document.getElementById("post-text").value.trim(),
            likes: document.getElementById("post-likes").value.trim(),
            dislikes: document.getElementById("post-dislikes").value.trim(),
            city: document.getElementById("post-city").value.trim(),
            state: document.getElementById("post-state").value.trim(),
            country: document.getElementById("post-country").value.trim(),
            hasMedia: document.getElementById("post-media").value.trim()
        },
        repost: {
            username: document.getElementById("repost-username").value.trim(),
            socialMedia: document.getElementById("repost-social").value.trim(),
            time: document.getElementById("repost-time").value.trim(),
            city: document.getElementById("repost-city").value.trim(),
            state: document.getElementById("repost-state").value.trim(),
            country: document.getElementById("repost-country").value.trim(),
            likes: document.getElementById("repost-likes").value.trim(),
            dislikes: document.getElementById("repost-dislikes").value.trim(),
            hasMedia: document.getElementById("repost-media").value.trim()
        }
    };

    console.log("Post submission:", postData);
    // Backend connection goes here???
});

// Add analysis parameters
document.getElementById("submit-analysis").addEventListener("click", () => {
    const analysisData = {
        projectName: document.getElementById("analysis-project-name").value.trim(),
        postUsername: document.getElementById("analysis-username").value.trim(),
        socialMedia: document.getElementById("analysis-social").value.trim(),
        timeOfPost: document.getElementById("analysis-time").value.trim(),
        fieldName: document.getElementById("analysis-field").value.trim(),
        result: document.getElementById("analysis-result").value.trim()
    };

    console.log("Analysis submission:", analysisData);
    // Backend connection goes here???
});

document.getElementById("toggle-repost").addEventListener("click", () => {
    const repostSection = document.getElementById("repost-section");
    repostSection.classList.toggle("hidden");
});
  

