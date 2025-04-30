const buttons = document.querySelectorAll('.entry-button');

const projectForm = document.getElementById('project-form');
const postForm = document.getElementById('post-form');
const analysisForm = document.getElementById('analysis-form');


buttons.forEach(button => {
    button.addEventListener('click', () => {
        const isSelected = button.classList.contains('selected');
  
        // Deselect all buttons
        buttons.forEach(btn => btn.classList.remove('selected'));
  
        // Hide all forms
        projectForm.classList.add('hidden');
        postForm.classList.add('hidden');
        analysisForm.classList.add('hidden');
  
        // If this wasn't already selected, select it and show the correct form
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
  

document.querySelector('.submit-btn').addEventListener('click', () => {
    // Validate & send form data to database
});
  

