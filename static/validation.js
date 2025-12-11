const form = document.querySelector('.admin-form');

form.addEventListener('submit', (event) => {
    const projectName = form.querySelector('input[name="project-name"]').value.trim();
    if (projectName === '') {
        event.preventDefault();
        alert('Project Name can\'t be empty.');
        return;
    }

    const description = form.querySelector('input[name="desc"]').value.trim();
    if (description === '') {
        event.preventDefault();
        alert('Project Description can\'t be empty.');
        return;
    }

    const imageInput = form.querySelector('input[name="project-img"]');
    if (imageInput.files.length === 0) {
        event.preventDefault();
        alert('Please upload a Project Image.');
        return;
    }
    
    const file = imageInput.files[0];
    const validImageTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validImageTypes.includes(file.type)) {
        event.preventDefault();
        alert('Please upload a valid image file (JPEG, PNG, GIF).');
        return;
    }
    
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
        event.preventDefault();
        alert('Image size must be less than 5MB.');
        return;
    }

    const projectLink = form.querySelector('input[name="project-url"]').value.trim();
    if (projectLink === '') {
        event.preventDefault();
        alert('Project Link can\'t be empty.');
        return;
    }
    if (!/^https?:\/\//i.test(projectLink)) {
        event.preventDefault();
        alert('Project Link must start with http:// or https://');
        return;
    }

    const githubLink = form.querySelector('input[name="project-github"]').value.trim();
    if (githubLink === '') {
        event.preventDefault();
        alert('GitHub Link can\'t be empty.');
        return;
    }
    if (!/^https?:\/\//i.test(githubLink)) {
        event.preventDefault();
        alert('GitHub Link must start with http:// or https://');
        return;
    }

    const techStack = form.querySelector('input[name="project-tech"]').value.trim();
    if (techStack === '') {
        event.preventDefault();
        alert('Tech Stack can\'t be empty.');
        return;
    }
});
