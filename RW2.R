
steps <- 100000
people <- 1000
starting_positions <- c(1, 5, 10, 20, 100)
left_probability <- 0.4

survival_prob <- function(starting_position) {
  # basic input validation
  if (!is.numeric(starting_position) || length(starting_position) != 1 || starting_position <= 0 || starting_position != as.integer(starting_position)) {
    stop("starting_position must be a single positive integer")
  }

  survival_peeps <- 0L

  for (i in seq_len(people)) {
    position <- as.integer(starting_position)
    alive <- TRUE

    for (step_idx in seq_len(steps)) {
      direction <- sample(c(-1L, 1L), 1, replace = TRUE, prob = c(left_probability, 1 - left_probability))
      position <- position + direction

      if (position == 0L) {
        alive <- FALSE
        break
      }
    }

    if (isTRUE(alive)) {
      survival_peeps <- survival_peeps + 1L
    }
  }

  prob <- survival_peeps / people
  return(as.numeric(prob))
}

prob1 <- sapply(starting_positions, survival_prob)
results <- data.frame(starting_position = starting_positions, probability = prob1)
print(results)













