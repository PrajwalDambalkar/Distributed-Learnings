// Step 1: Waiting for DOM to load and select the form
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    //Finding form by id
    const form = document.getElementById('Data236_HW1');
    
    // Step 2: Adding event listener for form submission
    form.addEventListener('submit', (event) => {
        // Alert for form submission & validation
        const content = form.content.value.trim();
        if (content.length <= 25) {
            alert('Blog content should be more than 25 characters');
            event.preventDefault();
            return;
        }

        // Validate checkbox for "Terms and conditions" 
        const termsChecked = form.terms.checked; 
        if (!termsChecked) {
            alert("You must agree to the terms and conditions");
            event.preventDefault();
            return;
        }

        // Conversion of form data into a JSON and logging it
        const fd = new FormData(form);
        const obj = Object.fromEntries(fd.entries());
        obj.terms = termsChecked; // Include checkbox state
        // Convert the object to a JSON string
        const jsonString = JSON.stringify(obj);
        console.log(jsonString);

        

    });
});