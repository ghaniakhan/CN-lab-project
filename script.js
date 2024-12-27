function previewAttachment(event) {
  const previewDiv = document.getElementById('attachment-preview');
  const file = event.target.files[0];
  
  // If no file is selected, clear the preview
  if (!file) {
      previewDiv.innerHTML = '';
      return;
  }

  // Create a preview based on the file type
  const fileReader = new FileReader();
  const fileName = file.name;
  const fileSize = (file.size / 1024).toFixed(2) + ' KB';

  fileReader.onload = function(e) {
      // For image files, show the image preview
      if (file.type.startsWith('image')) {
          previewDiv.innerHTML = `<img src="${e.target.result}" alt="Attachment Preview" style="max-width: 200px; max-height: 200px;">`;
      } else {
          previewDiv.innerHTML = `<p>File: ${fileName} (Size: ${fileSize})</p>`;
      }
  };

  fileReader.readAsDataURL(file);
}

// Handle the email template selection
document.getElementById('templates').addEventListener('change', function() {
  const template = this.value;
  if (template) {
      fetch(`/send-email?template=${template}`, { method: 'POST' })
          .then(response => response.json())
          .then(data => {
              document.getElementById('message').value = data.message; // Pre-populate the message with the template
          });
  }
});
