// 1. Build blogPost (spread + submissiondate)
// 2. Load old submissions: JSON.parse(localStorage.getItem("submissions") || "[]")
// 3. Push new blogPost into that array.
// 4. Save back with localStorage.setItem("submissions", JSON.stringify(array))
// 5. Call a renderSubmissions(array) function.

// Step 1: Waiting for DOM to load and select the form
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    //Finding form by id
    const form = document.getElementById('Data236_HW1'); // Form element
    const blogList = document.getElementById("blogList"); // Blog list container
    const clearBtn = document.getElementById("clearBlogSubmissions"); // Clear button

    const loadSubmissions = () => {
        try {
            const data = localStorage.getItem("submissions");
            return data ? JSON.parse(data) : [];
        } catch (error) {
            console.error("Error loading submissions:", error);
            return [];
        }
    };

    const saveSubmissions = (submissions) => {
        localStorage.setItem("submissions", JSON.stringify(submissions));
    };

    const renderSubmissions = (list) => {
        if (!Array.isArray(list)) list = [];

        blogList.innerHTML = ""; // Clear existing content
        list.forEach((post) => {
            const postElement = document.createElement("div");
            postElement.classList.add("blog-post"); // Add class for styling
            postElement.innerHTML = `
                <h3>${post.title}</h3>
                <p><strong>Author:</strong> ${post.name} | <strong>Email:</strong> ${post.email}</p>
                <p>${post.content}</p>
                <p><em>Category: ${post.category} | Submitted on: ${post.submissiondate}</em></p>
            `;
            blogList.appendChild(postElement);
        });
    }

    // (5) Defining counter function
    const makeSubmitCounter = () => {
        let count = Number(localStorage.getItem('submitCount') || 0);
        return () => {
            count++;
            localStorage.setItem('submitCount', count);
            return count;
        }
    }
    const nextSubmitCounter = makeSubmitCounter();

    renderSubmissions(loadSubmissions()); // Initial render

    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            localStorage.removeItem("submissions");
            renderSubmissions([]);
            console.log("Cleared all blog submissions");
        });
    }

    // Step 2: Adding event listener for form submission
    form.addEventListener('submit', (event) => {
        // (1a) Alert for form submission & validation
        const content = form.content.value.trim();
        if (content.length <= 25) {
            alert('Blog content should be more than 25 characters');
            event.preventDefault();
            return;
        }

        // (1b)Validate checkbox for "Terms and conditions" 
        const termsChecked = form.terms.checked; 
        if (!termsChecked) {
            alert("You must agree to the terms and conditions");
            event.preventDefault();
            return;
        }

        // (2) Conversion of form data into a JSON and logging it
        const fd = new FormData(form);
        const obj = Object.fromEntries(fd.entries());
        obj.terms = termsChecked; // Include checkbox state
        // Convert the object to a JSON string
        const jsonString = JSON.stringify(obj);
        console.log(jsonString);

        // (3) Destructure title and email
        const { title, email } = obj;
        console.log(`Title: ${title}, Email: ${email}`);

        // (4) Using spread operator to add "submissiondate"
        const blogPost = {
            ...obj,
            submissiondate: new Date().toISOString()
        };
        console.log(blogPost);

        const allSubmissions = loadSubmissions();
        allSubmissions.push(blogPost);
        saveSubmissions(allSubmissions);
        renderSubmissions(allSubmissions);

        // (5) Call the counter function and log the submission count
        const submitCounter = nextSubmitCounter();
        console.log(`Form submitted ${submitCounter} times`);

        event.preventDefault(); // Prevent actual form submission for demo purposes

        form.reset(); // Reset form after submission
        form.elements["title"]?.focus(); // Focus on the title input

    });
});