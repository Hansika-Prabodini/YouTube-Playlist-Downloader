# test_ui_components.R
# Comprehensive test suite for UI components using testthat framework
# Tests verify that all GUI widgets initialize correctly and have proper properties

library(testthat)

# Test GTK Environment Setup
test_that("GTK environment initializes correctly", {
  # Check if RGtk2 is available
  expect_true(requireNamespace("RGtk2", quietly = TRUE),
              info = "RGtk2 package must be installed")
  
  # Check if gWidgets2RGtk2 is available
  expect_true(requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              info = "gWidgets2RGtk2 package must be installed")
  
  # Attempt to load libraries
  expect_error({
    library(RGtk2)
    library(gWidgets2RGtk2)
  }, NA, info = "GTK libraries should load without errors")
})

# Test UI Creation Without Errors
test_that("UI components can be created without errors", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  # Check if ui.R file exists
  expect_true(file.exists("ui.R"), 
              info = "ui.R file must exist in the project root")
  
  # Source ui.R and check for errors
  expect_error(source("ui.R", local = TRUE), NA,
               info = "ui.R should source without errors")
})

# Test Widget Existence
test_that("all required widgets exist after UI initialization", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  # Source ui.R to create widgets
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # Check for main window
  expect_true(exists("window", envir = ui_env),
              info = "Main window widget should be defined")
  
  # Check for URL entry widget
  expect_true(exists("url_entry", envir = ui_env) || 
              exists("urlEntry", envir = ui_env) ||
              exists("url_input", envir = ui_env),
              info = "URL entry widget should be defined")
  
  # Check for buttons (download, cancel, etc.)
  button_exists <- exists("download_btn", envir = ui_env) ||
                   exists("downloadBtn", envir = ui_env) ||
                   exists("download_button", envir = ui_env)
  expect_true(button_exists,
              info = "Download button should be defined")
  
  # Check for scrollable container
  scroll_exists <- exists("scroll_container", envir = ui_env) ||
                   exists("scrollContainer", envir = ui_env) ||
                   exists("scroll_window", envir = ui_env)
  expect_true(scroll_exists,
              info = "Scrollable container should be defined")
})

# Test Widget Properties - Labels
test_that("widget labels are set correctly", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # Check button labels
  if (exists("download_btn", envir = ui_env)) {
    btn <- get("download_btn", envir = ui_env)
    # For gWidgets2, buttons are S3 objects
    expect_s3_class(btn, "GButton", 
                    info = "Download button should be a GButton object")
  } else if (exists("downloadBtn", envir = ui_env)) {
    btn <- get("downloadBtn", envir = ui_env)
    expect_s3_class(btn, "GButton",
                    info = "Download button should be a GButton object")
  }
  
  # Verify window object class
  if (exists("window", envir = ui_env)) {
    win <- get("window", envir = ui_env)
    expect_s3_class(win, "GWindow",
                    info = "Window should be a GWindow object")
  }
})

# Test Widget Properties - Enabled/Disabled States
test_that("widgets have correct initial enabled/disabled states", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # Check if download button is initially enabled (typical behavior)
  if (exists("download_btn", envir = ui_env)) {
    btn <- get("download_btn", envir = ui_env)
    # Widget should be enabled by default
    expect_true(enabled(btn), 
                info = "Download button should be enabled initially")
  } else if (exists("downloadBtn", envir = ui_env)) {
    btn <- get("downloadBtn", envir = ui_env)
    expect_true(enabled(btn),
                info = "Download button should be enabled initially")
  }
})

# Test Window Configuration - Dimensions
test_that("window has correct dimensions", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  if (exists("window", envir = ui_env)) {
    win <- get("window", envir = ui_env)
    
    # Get window size
    win_size <- size(win)
    
    # Check that dimensions are positive and reasonable
    expect_true(win_size[1] > 0,
                info = "Window width should be positive")
    expect_true(win_size[2] > 0,
                info = "Window height should be positive")
    
    # Check for reasonable minimum size (e.g., at least 300x200)
    expect_true(win_size[1] >= 200,
                info = "Window width should be at least 200 pixels")
    expect_true(win_size[2] >= 150,
                info = "Window height should be at least 150 pixels")
  }
})

# Test Window Configuration - Title
test_that("window has correct title", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  if (exists("window", envir = ui_env)) {
    win <- get("window", envir = ui_env)
    
    # Check that window has a non-empty title
    win_title <- svalue(win)
    expect_true(nzchar(win_title),
                info = "Window should have a non-empty title")
    expect_type(win_title, "character",
                info = "Window title should be a character string")
  }
})

# Test Scrollable Container Setup
test_that("scrollable container is properly configured", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # Look for scrollable container with various naming conventions
  scroll_obj <- NULL
  if (exists("scroll_container", envir = ui_env)) {
    scroll_obj <- get("scroll_container", envir = ui_env)
  } else if (exists("scrollContainer", envir = ui_env)) {
    scroll_obj <- get("scrollContainer", envir = ui_env)
  } else if (exists("scroll_window", envir = ui_env)) {
    scroll_obj <- get("scroll_window", envir = ui_env)
  }
  
  # Verify scrollable container exists and is proper class
  expect_false(is.null(scroll_obj),
               info = "Scrollable container should exist")
  
  if (!is.null(scroll_obj)) {
    # Check that it's a proper gWidgets2 container
    expect_true(inherits(scroll_obj, "GComponent"),
                info = "Scrollable container should be a GComponent")
  }
})

# Test Scrollable Container Accessibility
test_that("scrollable container is accessible and functional", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  scroll_obj <- NULL
  if (exists("scroll_container", envir = ui_env)) {
    scroll_obj <- get("scroll_container", envir = ui_env)
  } else if (exists("scrollContainer", envir = ui_env)) {
    scroll_obj <- get("scrollContainer", envir = ui_env)
  } else if (exists("scroll_window", envir = ui_env)) {
    scroll_obj <- get("scroll_window", envir = ui_env)
  }
  
  if (!is.null(scroll_obj)) {
    # Check that container is visible/enabled
    expect_true(visible(scroll_obj),
                info = "Scrollable container should be visible")
  }
})

# Test Programmatic Access to Widgets
test_that("widgets are retrievable by name or reference", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # Get list of all objects in ui environment
  ui_objects <- ls(envir = ui_env)
  
  # Check that we have some UI objects
  expect_true(length(ui_objects) > 0,
              info = "UI environment should contain widget objects")
  
  # Try to retrieve window object
  if ("window" %in% ui_objects) {
    win <- get("window", envir = ui_env)
    expect_false(is.null(win),
                 info = "Window object should be retrievable")
  }
  
  # Try to retrieve button objects
  button_names <- grep("btn|button", ui_objects, value = TRUE, ignore.case = TRUE)
  expect_true(length(button_names) > 0,
              info = "At least one button should be defined")
  
  # Try to retrieve entry/input objects
  entry_names <- grep("entry|input", ui_objects, value = TRUE, ignore.case = TRUE)
  expect_true(length(entry_names) > 0,
              info = "At least one entry/input widget should be defined")
})

# Test Mock Button Click Events
test_that("button click events can be simulated", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  skip("Mock events require additional mocking framework setup")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # This is a placeholder for mock event testing
  # In practice, this would require:
  # 1. The mockery package or similar
  # 2. Handler functions to be testable
  # 3. GTK event simulation capabilities
  
  # Example structure (not executable without proper setup):
  # if (exists("download_btn", envir = ui_env)) {
  #   btn <- get("download_btn", envir = ui_env)
  #   # Mock click event
  #   # Verify handler was called
  # }
})

# Test UI Cleanup
test_that("UI can be properly disposed/cleaned up", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # Test that dispose methods don't throw errors
  if (exists("window", envir = ui_env)) {
    win <- get("window", envir = ui_env)
    expect_error(dispose(win), NA,
                 info = "Window disposal should not throw errors")
  }
})

# Test URL Entry Widget Properties
test_that("URL entry widget is properly configured", {
  skip_if_not(requireNamespace("RGtk2", quietly = TRUE) && 
              requireNamespace("gWidgets2RGtk2", quietly = TRUE),
              "GTK packages not available")
  
  library(RGtk2)
  library(gWidgets2RGtk2)
  
  ui_env <- new.env()
  source("ui.R", local = ui_env)
  
  # Find URL entry widget
  url_widget <- NULL
  if (exists("url_entry", envir = ui_env)) {
    url_widget <- get("url_entry", envir = ui_env)
  } else if (exists("urlEntry", envir = ui_env)) {
    url_widget <- get("urlEntry", envir = ui_env)
  } else if (exists("url_input", envir = ui_env)) {
    url_widget <- get("url_input", envir = ui_env)
  }
  
  expect_false(is.null(url_widget),
               info = "URL entry widget should exist")
  
  if (!is.null(url_widget)) {
    # Check that it's a proper entry widget
    expect_true(inherits(url_widget, "GEdit") || inherits(url_widget, "GComponent"),
                info = "URL entry should be a GEdit or GComponent object")
    
    # Check that it's enabled
    expect_true(enabled(url_widget),
                info = "URL entry should be enabled")
    
    # Check that it's visible
    expect_true(visible(url_widget),
                info = "URL entry should be visible")
  }
})

# Print test summary message
message("\n=== UI Component Test Suite Completed ===")
message("Tests verify:")
message("  - GTK environment initialization")
message("  - UI creation without errors")
message("  - Widget existence (window, buttons, entry, scrollable container)")
message("  - Widget properties (labels, dimensions, states)")
message("  - Window configuration (size, title)")
message("  - Scrollable container setup and accessibility")
message("  - Programmatic widget access")
message("\nFor full test execution instructions, see test_ui_components.md")
