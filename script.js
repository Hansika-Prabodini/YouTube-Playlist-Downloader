/**
 * Calculator JavaScript Implementation
 * Provides core calculation functionality with proper number handling
 */

// Constants for better maintainability
const INPUT_FIELD_1_ID = 'number1';
const INPUT_FIELD_2_ID = 'number2';
const RESULT_CONTAINER_ID = 'result';
const CALCULATE_BUTTON_ID = 'calculateBtn';

// JavaScript safe integer limits
const MAX_SAFE_INTEGER = Number.MAX_SAFE_INTEGER; // 9007199254740991
const MIN_SAFE_INTEGER = Number.MIN_SAFE_INTEGER; // -9007199254740991

/**
 * Retrieves values from both input fields by ID
 * @returns {Object} Object containing both input values as strings
 */
function getInputValues() {
    const input1 = document.getElementById(INPUT_FIELD_1_ID);
    const input2 = document.getElementById(INPUT_FIELD_2_ID);
    
    if (!input1 || !input2) {
        throw new Error('Input fields not found. Please check that HTML elements with correct IDs exist.');
    }
    
    return {
        value1: input1.value.trim(),
        value2: input2.value.trim()
    };
}

/**
 * Parses and validates numeric input with support for decimals and negative numbers
 * @param {string} input - Raw input string
 * @returns {number} Parsed number or NaN if invalid
 */
function parseNumericInput(input) {
    if (!input || input === '') {
        return NaN;
    }
    
    // Use parseFloat to handle decimals and negative numbers
    const parsed = parseFloat(input);
    
    // Additional validation for edge cases
    if (isNaN(parsed) || !isFinite(parsed)) {
        return NaN;
    }
    
    return parsed;
}

/**
 * Performs addition calculation with proper numeric handling
 * @param {number} num1 - First number
 * @param {number} num2 - Second number
 * @returns {number} Result of addition
 */
function performAddition(num1, num2) {
    if (isNaN(num1) || isNaN(num2)) {
        throw new Error('Invalid numbers provided for calculation');
    }
    
    const result = num1 + num2;
    
    // Handle infinity cases
    if (!isFinite(result)) {
        return result;
    }
    
    return result;
}

/**
 * Handles JavaScript number precision limitations
 * @param {number} result - Raw calculation result
 * @returns {number} Result with precision handling applied
 */
function handlePrecision(result) {
    // For very large numbers outside safe integer range, keep as-is
    if (Math.abs(result) > MAX_SAFE_INTEGER) {
        return result;
    }
    
    // For decimal numbers, handle floating point precision issues
    // Round to 10 decimal places to avoid floating point artifacts
    if (result % 1 !== 0) {
        return Math.round(result * Math.pow(10, 10)) / Math.pow(10, 10);
    }
    
    return result;
}

/**
 * Formats result for display with proper handling of large numbers and scientific notation
 * @param {number} result - Calculation result
 * @returns {string} Formatted result string
 */
function formatResultDisplay(result) {
    if (isNaN(result)) {
        return 'Error: Invalid input';
    }
    
    if (result === Infinity) {
        return 'Infinity';
    }
    
    if (result === -Infinity) {
        return '-Infinity';
    }
    
    // Handle very large numbers - use scientific notation for readability
    if (Math.abs(result) >= 1e15) {
        return result.toExponential(6);
    }
    
    // Handle very small decimal numbers - use scientific notation
    if (Math.abs(result) < 1e-6 && result !== 0) {
        return result.toExponential(6);
    }
    
    // For normal range numbers, format appropriately
    if (result % 1 === 0) {
        // Integer result
        return result.toString();
    } else {
        // Decimal result - limit to reasonable decimal places
        const formatted = result.toString();
        
        // If the number has many decimal places, limit to 10
        if (formatted.includes('.') && formatted.split('.')[1].length > 10) {
            return result.toFixed(10).replace(/\.?0+$/, '');
        }
        
        return formatted;
    }
}

/**
 * Updates the DOM to display calculation results
 * @param {string} formattedResult - Formatted result string to display
 */
function displayResult(formattedResult) {
    const resultContainer = document.getElementById(RESULT_CONTAINER_ID);
    
    if (!resultContainer) {
        throw new Error('Result container not found. Please check that HTML element with correct ID exists.');
    }
    
    resultContainer.textContent = formattedResult;
}

/**
 * Main calculation function that orchestrates the entire process
 * Called when the Calculate button is clicked
 */
function calculate() {
    try {
        // Step 1: Retrieve input values
        const inputs = getInputValues();
        
        // Step 2: Parse and validate inputs
        const num1 = parseNumericInput(inputs.value1);
        const num2 = parseNumericInput(inputs.value2);
        
        // Step 3: Validate that both inputs are valid numbers
        if (isNaN(num1)) {
            displayResult('Error: First number is not valid');
            return;
        }
        
        if (isNaN(num2)) {
            displayResult('Error: Second number is not valid');
            return;
        }
        
        // Step 4: Perform calculation
        const rawResult = performAddition(num1, num2);
        
        // Step 5: Handle precision issues
        const precisionHandledResult = handlePrecision(rawResult);
        
        // Step 6: Format for display
        const formattedResult = formatResultDisplay(precisionHandledResult);
        
        // Step 7: Display result
        displayResult(formattedResult);
        
    } catch (error) {
        console.error('Calculation error:', error);
        displayResult('Error: ' + error.message);
    }
}

/**
 * Initialize the calculator when the DOM is loaded
 * Sets up event listeners and ensures proper functionality
 */
function initializeCalculator() {
    // Ensure DOM is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCalculator);
        return;
    }
    
    // Find the calculate button
    const calculateButton = document.getElementById(CALCULATE_BUTTON_ID);
    
    if (!calculateButton) {
        console.warn('Calculate button not found. Calculator will not be functional.');
        return;
    }
    
    // Add click event listener to ensure calculation only occurs on button click
    calculateButton.addEventListener('click', calculate);
    
    // Optional: Allow Enter key in input fields to trigger calculation
    const input1 = document.getElementById(INPUT_FIELD_1_ID);
    const input2 = document.getElementById(INPUT_FIELD_2_ID);
    
    if (input1) {
        input1.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                calculate();
            }
        });
    }
    
    if (input2) {
        input2.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                calculate();
            }
        });
    }
}

// Initialize calculator when script loads
initializeCalculator();

// Export functions for testing (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getInputValues,
        parseNumericInput,
        performAddition,
        handlePrecision,
        formatResultDisplay,
        displayResult,
        calculate,
        initializeCalculator
    };
}
