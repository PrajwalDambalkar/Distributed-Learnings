// Step 1: Waiting for DOM to load and select the form
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    //Finding form by id
    const form = document.getElementById('Data236_HW1');
    
    // Step 2: Adding event listener for form submission
    form.addEventListener('submit', (event) => {
        const content = form.content.value.trim();
        if (content.length <= 25) {
            alert('Blog content should be more than 25 characters');
            event.preventDefault();
            return;
        }
        
    });
});