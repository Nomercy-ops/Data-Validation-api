function initializeValidationForm() {
  const elements = cacheDOMElements();
  addEventListeners(elements);



  function cacheDOMElements() {
    // Cache DOM elements
    const elements = {
      startValidationButton: document.getElementById('start-validation-button'),
      progressBarContainer: document.getElementById('progress-bar-container'),
      progressBar: document.querySelector('.progress-bar .progress'),
      sourceElement: document.getElementById('source'),
      targetElement: document.getElementById('target'),
      csvFieldsElement: document.getElementById('source-csv-fields'),
      sourceDbFieldsElement: document.getElementById('source-database-fields'),
      targetCsvFieldsElement: document.getElementById('target-csv-fields'),
      targetDbFieldsElement: document.getElementById('target-database-fields'),

    };

    return elements;
  }

  function addEventListeners(elements) {
    const ids = {
      startValidationButton: 'start-validation-button',
      resetButton: 'reset-button',
      validationForm: 'validation-form'
    };

    const element = Object.keys(ids).reduce((acc, key) => {
      acc[key] = document.getElementById(ids[key]);
      return acc;
    }, {});

    element.startValidationButton.addEventListener('click', (event) => handleValidation(event, elements));
    element.resetButton.addEventListener('click', handleReset);
    element.validationForm.addEventListener('change', handleSourceTargetChange);
  }


  function handleValidation(event) {
    event.preventDefault(); // Prevent form submission

    const selectedDataSource = elements.sourceElement.value;
    const selectedTarget = elements.targetElement.value;

    if (!selectedDataSource || !selectedTarget) {
      alert('Please select a valid data source and target.');
      return;
    }

    if (selectedDataSource === 'csv') {
      const selectedSourceFile = document.getElementById('source-csv-file');
      if (!selectedSourceFile.files.length) {
        alert('Please select a CSV file for the source.');
        return;
      }
    } else if (selectedDataSource === 'database') {
      if (!isDatabaseDetailsProvided('source')) {
        alert('Please provide all the required database details for the source.');
        return; // Stop further execution
      }
    }

    if (selectedTarget === 'csv') {
      const selectedTargetFile = document.getElementById('target-csv-file');
      if (!selectedTargetFile.files.length) {
        alert('Please select a CSV file for the target.');
        return;
      }
    } else if (selectedTarget === 'database') {
      if (!isDatabaseDetailsProvided('target')) {
        alert('Please provide all the required database details for the target.');
        return; // Stop further execution
      }
    }

    const form = createForm(selectedDataSource, selectedTarget);
    document.body.appendChild(form);
    submitForm(form);
  }

  function isDatabaseDetailsProvided(type) {
    const host = document.getElementById(`${type}-database-host`).value;
    const name = document.getElementById(`${type}-database-name`).value;
    const username = document.getElementById(`${type}-database-username`).value;
    const password = document.getElementById(`${type}-database-password`).value;

    return host !== '' && name !== '' && username !== '' && password !== '';
  }

function getSelectedValue(id) {
  const radioButtons = Array.from(document.getElementsByName(id));
  const selectedRadioButton = radioButtons.find(button => button.checked);
  return selectedRadioButton ? selectedRadioButton.value : "";
}


  function createForm(selectedDataSource, selectedTarget) {
    const form = document.createElement('form');
    form.action = getValidationEndpoint(selectedDataSource, selectedTarget);
    form.method = 'POST';
  
    if (selectedDataSource === 'csv') {
      form.enctype = 'multipart/form-data';
  
      form.appendChild(createHiddenInput('source', selectedDataSource));
      form.appendChild(createHiddenInput('target', selectedTarget));
  
      const sourceFileInput = createFileInput('source_csv', document.getElementById('source-csv-file').files);
      form.appendChild(sourceFileInput);
  
      if (selectedTarget === 'csv') {
        const targetFileInput = createFileInput('target_csv', document.getElementById('target-csv-file').files);
        form.appendChild(targetFileInput);
      }
    } else if (selectedDataSource === 'database') {
      form.enctype = 'application/json';
  
      const formData = {
        // 'source': selectedDataSource,
        // 'target': selectedTarget,
        'source_db': {
          'host': document.getElementById('source-database-host').value,
          'database-name': document.getElementById('source-database-name').value,
          'username': document.getElementById('source-database-username').value,
          'password': document.getElementById('source-database-password').value,
          'source-database-type':getSelectedValue('source_database_type')
        }
      };
  
      if (selectedTarget === 'database') {
        formData['target_db'] = {
          'host': document.getElementById('target-database-host').value,
          'database-name': document.getElementById('target-database-name').value,
          'username': document.getElementById('target-database-username').value,
          'password': document.getElementById('target-database-password').value,
          'target-database-type':getSelectedValue('target_database_type')
        };
      }
  
      const jsonData = JSON.stringify(formData);
      console.log(jsonData);
      const jsonInput = createHiddenInput('data', jsonData);
      form.appendChild(jsonInput);
  
      // Add hidden input elements for source and target
      form.appendChild(createHiddenInput('source', selectedDataSource));
      form.appendChild(createHiddenInput('target', selectedTarget));
    }
  
    return form;
  }
  
  


  function getValidationEndpoint(selectedSource, selectedTarget) {
    const endpoints = {
      csvcsv: '/validate/csv',
      databasedatabase: '/validate/database',
    };

    return endpoints[selectedSource + selectedTarget] || '/validate';
  }

  function createHiddenInput(name, value) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;
    return input;
  }

  function createFileInput(name, files) {
    const input = document.createElement('input');
    input.type = 'file';
    input.name = name;
    if (files) {
      input.files = files;
    }
    return input;
  }


  function submitForm(form) {
    console.log(form)
    const formContainer = document.createElement('div');
    formContainer.hidden = true;
    formContainer.style.display = 'none';
    formContainer.appendChild(form);
    document.body.appendChild(formContainer);

    const startValidationButton = document.getElementById('start-validation-button');
    const progressBarContainer = document.getElementById('progress-bar-container');
    const progressBar = document.querySelector('.progress-bar .progress');

    startValidationButton.style.display = 'none';
    progressBarContainer.style.display = 'block';

    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      progressBar.style.width = progress + '%';
      progressBar.textContent = progress + '%';

      if (progress >= 100) {
        clearInterval(interval);
        setTimeout(() => {
          console.log('Submitting form for validation...');
          form.submit();
          document.body.removeChild(formContainer);
        }, 1500);
      }
    }, 100);
  }




  function handleReset() {
    elements.sourceElement.value = '';
    elements.csvFieldsElement.value = '';
    elements.sourceDbFieldsElement.value = '';

    elements.targetElement.value = '';
    elements.targetCsvFieldsElement.value = '';
    elements.targetDbFieldsElement.value = '';
  }

  function handleSourceTargetChange(event) {
    const selectedElement = event.target;
    const selectedValue = selectedElement.value;

    if (selectedElement === elements.sourceElement) {
      handleFileFields(selectedValue, 'source');
    } else if (selectedElement === elements.targetElement) {
      handleFileFields(selectedValue, 'target');
    }
  }

  function handleFileFields(selectedValue, fileType) {
    const fileFields = ['csv'];
    const databaseFields = ['database'];

    const csvFieldsElement = document.getElementById(`${fileType}-csv-fields`);
    const databaseFieldsElement = document.getElementById(`${fileType}-database-fields`);

    if (fileFields.includes(selectedValue)) {
      csvFieldsElement.style.display = 'block';
      databaseFieldsElement.style.display = 'none';
    } else if (databaseFields.includes(selectedValue)) {
      csvFieldsElement.style.display = 'none';
      databaseFieldsElement.style.display = 'block';
    } else {
      csvFieldsElement.style.display = 'none';
      databaseFieldsElement.style.display = 'none';
    }
  }



}
// Call the initialization function
initializeValidationForm();
