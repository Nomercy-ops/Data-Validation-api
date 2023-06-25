// document.getElementById('start-validation-button').addEventListener('click', function () {
//   const selectedDataSource = document.getElementById('source').value;
//   const selectedTarget = document.getElementById('target').value;

//   // Check if source and target are selected
//   if (selectedDataSource === '' || selectedTarget === '') {
//     alert('Please select a valid data source and target.');
//     return; // Stop further execution
//   }

//   if (selectedDataSource === 'csv' && !document.getElementById('csv-file').files.length) {
//     alert('Please select a CSV file for the source.');
//     return; // Stop further execution
//   }
  
//   if (selectedTarget === 'csv' && !document.getElementById('target-csv-file').files.length) {
//     alert('Please select a CSV file for the target.');
//     return; // Stop further execution
//   }
  
//   // Set the form's enctype attribute to "multipart/form-data"
//   const form = document.getElementById('validation-form');
//   form.enctype = 'multipart/form-data';

//   // Display processing message
//   const progressMessage = document.getElementById('progress-message');
//   progressMessage.textContent = 'Validation in progress...';

//   // Show progress bar
//   const progressBar = document.getElementById('progress-bar');
//   progressBar.style.display = 'block';

//   // Simulate validation progress
//   let progress = 0;
//   const interval = setInterval(() => {
//     progress += 10;
//     progressBar.style.width = progress + '%';

//     if (progress >= 100) {
//       clearInterval(interval);
//       progressMessage.textContent = 'Validation complete. Please wait...';
//       form.submit(); // Submit the form for validation
//     }
//   }, 500);
// });


document.getElementById('start-validation-button').addEventListener('click', function () {
  const selectedDataSource = document.getElementById('source').value;
  const selectedTarget = document.getElementById('target').value;

  // Check if source and target are selected
  if (selectedDataSource === '' || selectedTarget === '') {
    alert('Please select a valid data source and target.');
    return; // Stop further execution
  }

  // Get the file data for source_csv if selectedDataSource is 'csv'
  let sourceCsvFileData = null;
  if (selectedDataSource === 'csv') {
    const sourceCsvFileInput = document.getElementById('csv-file');
    if (sourceCsvFileInput.files.length === 0) {
      alert('Please select a CSV file for the source.');
      return; // Stop further execution
    }
    sourceCsvFileData = sourceCsvFileInput.files[0];
  }

  // Get the file data for target_csv if selectedTarget is 'csv'
  let targetCsvFileData = null;
  if (selectedTarget === 'csv') {
    const targetCsvFileInput = document.getElementById('target-csv-file');
    if (targetCsvFileInput.files.length === 0) {
      alert('Please select a CSV file for the target.');
      return; // Stop further execution
    }
    targetCsvFileData = targetCsvFileInput.files[0];
  }

  // Set the form's enctype attribute to "multipart/form-data"
  const form = document.getElementById('validation-form');
  form.enctype = 'multipart/form-data';


  // Display processing message
  const progressMessage = document.getElementById('progress-message');
  progressMessage.textContent = 'Validation in progress...';

  // Show progress bar
  const progressBar = document.getElementById('progress-bar');
  progressBar.style.display = 'block';

  // Simulate validation progress
  let progress = 0;
  const interval = setInterval(() => {
    progress += 10;
    progressBar.style.width = progress + '%';

    if (progress >= 100) {
      clearInterval(interval);
      progressMessage.textContent = 'Validation complete. Please wait...';
      // Submit the form with the updated formData
      fetch('/confirm', {
        method: 'POST',
        body: formData
      }).then(response => {
        // Handle the response
      }).catch(error => {
        // Handle errors
      });
    }
  }, 500);
});

//Rest of the code...
document.getElementById('reset-button').addEventListener('click', function () {
  // Reset the form fields
  document.getElementById('source').value = '';
  document.getElementById('csv-file').value = '';
  document.getElementById('database-host').value = '';
  document.getElementById('database-name').value = '';
  document.getElementById('database-username').value = '';
  document.getElementById('database-password').value = '';
  document.getElementById('target').value = '';
  document.getElementById('target-csv-file').value = '';
  document.getElementById('target-database-host').value = '';
  document.getElementById('target-database-name').value = '';
  document.getElementById('target-database-username').value = '';
  document.getElementById('target-database-password').value = '';
});

// Show/hide fields based on selected source
document.getElementById('source').addEventListener('change', function () {
  const selectedSource = this.value;

  if (selectedSource === 'csv') {
    document.getElementById('csv-fields').style.display = 'block';
    document.getElementById('database-fields').style.display = 'none';
  } else if (selectedSource === 'database') {
    document.getElementById('csv-fields').style.display = 'none';
    document.getElementById('database-fields').style.display = 'block';
  } else {
    document.getElementById('csv-fields').style.display = 'none';
    document.getElementById('database-fields').style.display = 'none';
  }
});

// Show/hide fields based on selected target
document.getElementById('target').addEventListener('change', function () {
  const selectedTarget = this.value;

  if (selectedTarget === 'csv') {
    document.getElementById('target-csv-fields').style.display = 'block';
    document.getElementById('target-database-fields').style.display = 'none';
  } else if (selectedTarget === 'database') {
    document.getElementById('target-csv-fields').style.display = 'none';
    document.getElementById('target-database-fields').style.display = 'block';
  } else {
    document.getElementById('target-csv-fields').style.display = 'none';
    document.getElementById('target-database-fields').style.display = 'none';
  }
});