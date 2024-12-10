# Install necessary packages
install.packages(c("poweRlaw", "parallel", "ggplot2", "png"))

# Load libraries
library("poweRlaw")
library("ggplot2")
library("parallel")
library("png")

# Create a directory for saving plots
dir.create("Power Law Plots", showWarnings = FALSE)

# Read in the data from CSV files
readfile_chem <- read.csv("OA_REDO_ChemAgeMatch_2023.11.02.csv")
readfile_comp <- read.csv("OA_REDO_CompAgeMatch_2023.11.02.csv")

# List of variables to analyze
variables <- c("Scopus1", "tweet1", "reader1")

# File path where the plots will be saved
file_path <- "Power Law Plots"

# Mapping of code names to plot names
variable_names <- c("Scopus1" = "Citations", "tweet1" = "Tweets", "reader1" = "Readers")

# Function to process data
process_data <- function(data, var_name) {
  data_var <- data[[var_name]]
  data_pl <- displ$new(data_var)
  data_ln <- dislnorm$new(data_var)
  data_exp <- disexp$new(data_var)
  
  est_pl <- estimate_xmin(data_pl)
  est_ln <- estimate_xmin(data_ln)
  est_exp <- estimate_xmin(data_exp)
  
  data_pl$setXmin(est_pl)
  data_ln$setXmin(est_ln)
  data_exp$setXmin(est_exp)
  
  list(pl = data_pl, ln = data_ln, exp = data_exp)
}

# Process ChemRxiv and Control data
results_chem <- lapply(variables, process_data, data = readfile_chem)
results_comp <- lapply(variables, process_data, data = readfile_comp)

# Extract xmin and pars for ChemRxiv data
xmin_chem <- lapply(results_chem, function(res) {
  list(pl = res$pl$getXmin(), ln = res$ln$getXmin(), exp = res$exp$getXmin())
})

pars_chem <- lapply(results_chem, function(res) {
  list(pl = res$pl$getPars(), ln = res$ln$getPars(), exp = res$exp$getPars())
})

# Extract xmin and pars for Control data
xmin_comp <- lapply(results_comp, function(res) {
  list(pl = res$pl$getXmin(), ln = res$ln$getXmin(), exp = res$exp$getXmin())
})

pars_comp <- lapply(results_comp, function(res) {
  list(pl = res$pl$getPars(), ln = res$ln$getPars(), exp = res$exp$getPars())
})

# Print xmin and pars for inspection
print("ChemRxiv data xmin:")
print(xmin_chem)
print("ChemRxiv data pars:")
print(pars_chem)
print("Control data xmin:")
print(xmin_comp)
print("Control data pars:")
print(pars_comp)

# Bootstrap function
bootstrap_data <- function(res, threads = 32, sims = 2500) {
  list(
    pl = bootstrap(res$pl, no_of_sims = sims, threads = threads, seed = 1),
    ln = bootstrap(res$ln, no_of_sims = sims, threads = threads, seed = 1),
    exp = bootstrap(res$exp, no_of_sims = sims, threads = threads, seed = 1)
  )
}

# Bootstrap ChemRxiv and Control data
bs_chem <- lapply(results_chem, bootstrap_data)
bs_comp <- lapply(results_comp, bootstrap_data)

# Calculate standard deviations
calc_sd <- function(bs) {
  sapply(bs, function(b) sd(b$bootstraps[, 2]))
}

sds_chem <- lapply(bs_chem, calc_sd)
sds_comp <- lapply(bs_comp, calc_sd)

# Perform bootstrap p-value analysis
bootstrap_p_data <- function(res, threads = 32, sims = 2500) {
  list(
    pl = bootstrap_p(res$pl, no_of_sims = sims, threads = threads, seed = 1),
    ln = bootstrap_p(res$ln, no_of_sims = sims, threads = threads, seed = 1),
    exp = bootstrap_p(res$exp, no_of_sims = sims, threads = threads, seed = 1)
  )
}

bs_p_chem <- lapply(results_chem, bootstrap_p_data)
bs_p_comp <- lapply(results_comp, bootstrap_p_data)

# Print p-values from bootstrap analysis
print_p_values <- function(bs_p) {
  sapply(bs_p, function(b) list(pl = b$pl$p, ln = b$ln$p, exp = b$exp$p))
}

p_values_chem <- print_p_values(bs_p_chem)
p_values_comp <- print_p_values(bs_p_comp)

# Print p-values for inspection
print("ChemRxiv data p-values:")
print(p_values_chem)
print("Control data p-values:")
print(p_values_comp)

# Define the plot_and_save_A function with the correct plotting methods
plot_and_save_A <- function(results_chem, results_comp, plot_index_start) {
  plot_index <- plot_index_start
  
  lapply(seq_along(variables), function(i) {
    var_name <- variables[i]
    plot_name <- variable_names[[var_name]]
    
    # ChemRxiv Power Law plot
    png(filename = file.path(file_path, paste0("Fig_A", plot_index, "_chem_", plot_name, "_pl.png")),
        width = 1600, height = 1200, res = 200)
    tryCatch({
      plot(results_chem[[i]]$pl, main = paste0("Fig. A", plot_index, " - ChemRxiv - ", plot_name, " - Power Law"), col = "black")
      lines(results_chem[[i]]$pl, col = "black", lwd = 2)
      dev.off()
    }, error = function(e) {
      dev.off()
      print(paste("Error in ChemRxiv Power Law plot for variable:", var_name))
      print(e)
    })
    plot_index <<- plot_index + 1
    
    # Control Power Law plot
    png(filename = file.path(file_path, paste0("Fig_A", plot_index, "_comp_", plot_name, "_pl.png")),
        width = 1600, height = 1200, res = 200)
    tryCatch({
      plot(results_comp[[i]]$pl, main = paste0("Fig. A", plot_index, " - Control - ", plot_name, " - Power Law"), col = "black")
      lines(results_comp[[i]]$pl, col = "black", lwd = 2)
      dev.off()
    }, error = function(e) {
      dev.off()
      print(paste("Error in Control Power Law plot for variable:", var_name))
      print(e)
    })
    plot_index <<- plot_index + 1
    
    # ChemRxiv Log-Normal plot
    png(filename = file.path(file_path, paste0("Fig_A", plot_index, "_chem_", plot_name, "_ln.png")),
        width = 1600, height = 1200, res = 200)
    tryCatch({
      plot(results_chem[[i]]$ln, main = paste0("Fig. A", plot_index, " - ChemRxiv - ", plot_name, " - Log-Normal"), col = "black")
      lines(results_chem[[i]]$ln, col = "black", lwd = 2)
      dev.off()
    }, error = function(e) {
      dev.off()
      print(paste("Error in ChemRxiv Log-Normal plot for variable:", var_name))
      print(e)
    })
    plot_index <<- plot_index + 1
    
    # Control Log-Normal plot
    png(filename = file.path(file_path, paste0("Fig_A", plot_index, "_comp_", plot_name, "_ln.png")),
        width = 1600, height = 1200, res = 200)
    tryCatch({
      plot(results_comp[[i]]$ln, main = paste0("Fig. A", plot_index, " - Control - ", plot_name, " - Log-Normal"), col = "black")
      lines(results_comp[[i]]$ln, col = "black", lwd = 2)
      dev.off()
    }, error = function(e) {
      dev.off()
      print(paste("Error in Control Log-Normal plot for variable:", var_name))
      print(e)
    })
    plot_index <<- plot_index + 1
    
    # ChemRxiv Exponential plot
    png(filename = file.path(file_path, paste0("Fig_A", plot_index, "_chem_", plot_name, "_exp.png")),
        width = 1600, height = 1200, res = 200)
    tryCatch({
      plot(results_chem[[i]]$exp, main = paste0("Fig. A", plot_index, " - ChemRxiv - ", plot_name, " - Exponential"), col = "black")
      lines(results_chem[[i]]$exp, col = "black", lwd = 2)
      dev.off()
    }, error = function(e) {
      dev.off()
      print(paste("Error in ChemRxiv Exponential plot for variable:", var_name))
      print(e)
    })
    plot_index <<- plot_index + 1
    
    # Control Exponential plot
    png(filename = file.path(file_path, paste0("Fig_A", plot_index, "_comp_", plot_name, "_exp.png")),
        width = 1600, height = 1200, res = 200)
    tryCatch({
      plot(results_comp[[i]]$exp, main = paste0("Fig. A", plot_index, " - Control - ", plot_name, " - Exponential"), col = "black")
      lines(results_comp[[i]]$exp, col = "black", lwd = 2)
      dev.off()
    }, error = function(e) {
      dev.off()
      print(paste("Error in Control Exponential plot for variable:", var_name))
      print(e)
    })
    plot_index <<- plot_index + 1
  })
  
  return(plot_index)
}

# Plotting Function Call for Appendix A
plot_index_A <- plot_and_save_A(results_chem, results_comp, 1)




# Plot bootstrap results and save as PNG for Appendix B
plot_bootstraps_and_save_B <- function(bs_chem, bs_comp, plot_index_start) {
  plot_index <- plot_index_start  # Initialize the plot index
  
  for (i in seq_along(variables)) {
    var_name <- variables[i]
    plot_name <- variable_names[[var_name]]
    
    # ChemRxiv Power Law bootstrap plot
    png(filename = file.path(file_path, paste0("Fig_B", plot_index, "_chem_", plot_name, "_pl_bootstrap.png")),
        width = 1600, height = 1200, res = 200)
    plot(bs_chem[[i]]$pl, main = paste0("Fig. B", plot_index, " - ChemRxiv - ", plot_name, " - Power Law Bootstrap"))
    dev.off()
    plot_index <- plot_index + 1
    
    # ChemRxiv Log-Normal bootstrap plot
    png(filename = file.path(file_path, paste0("Fig_B", plot_index, "_chem_", plot_name, "_ln_bootstrap.png")),
        width = 1600, height = 1200, res = 200)
    plot(bs_chem[[i]]$ln, main = paste0("Fig. B", plot_index, " - ChemRxiv - ", plot_name, " - Log-Normal Bootstrap"))
    dev.off()
    plot_index <- plot_index + 1
    
    # ChemRxiv Exponential bootstrap plot
    png(filename = file.path(file_path, paste0("Fig_B", plot_index, "_chem_", plot_name, "_exp_bootstrap.png")),
        width = 1600, height = 1200, res = 200)
    plot(bs_chem[[i]]$exp, main = paste0("Fig. B", plot_index, " - ChemRxiv - ", plot_name, " - Exponential Bootstrap"))
    dev.off()
    plot_index <- plot_index + 1
    
    # Control Power Law bootstrap plot
    png(filename = file.path(file_path, paste0("Fig_B", plot_index, "_comp_", plot_name, "_pl_bootstrap.png")),
        width = 1600, height = 1200, res = 200)
    plot(bs_comp[[i]]$pl, main = paste0("Fig. B", plot_index, " - Control - ", plot_name, " - Power Law Bootstrap"))
    dev.off()
    plot_index <- plot_index + 1
    
    # Control Log-Normal bootstrap plot
    png(filename = file.path(file_path, paste0("Fig_B", plot_index, "_comp_", plot_name, "_ln_bootstrap.png")),
        width = 1600, height = 1200, res = 200)
    plot(bs_comp[[i]]$ln, main = paste0("Fig. B", plot_index, " - Control - ", plot_name, " - Log-Normal Bootstrap"))
    dev.off()
    plot_index <- plot_index + 1
    
    # Control Exponential bootstrap plot
    png(filename = file.path(file_path, paste0("Fig_B", plot_index, "_comp_", plot_name, "_exp_bootstrap.png")),
        width = 1600, height = 1200, res = 200)
    plot(bs_comp[[i]]$exp, main = paste0("Fig. B", plot_index, " - Control - ", plot_name, " - Exponential Bootstrap"))
    dev.off()
    plot_index <- plot_index + 1
  }
  
  return(plot_index)
}

# Plotting Function Call for Appendix B
plot_index_B <- 1

# Grouped by metrics
plot_index_B <- plot_bootstraps_and_save_B(bs_chem, bs_comp, plot_index_B)


# Create histograms of bootstrap results and save as PNG for Appendix C
plot_histograms_and_save_C <- function(bs, prefix, plot_index_start) {
  plot_index <- plot_index_start  # Initialize the plot index
  lapply(seq_along(bs), function(i) {
    var_name <- variables[i]
    plot_name <- variable_names[[var_name]]
    
    # Power Law histogram
    png(filename = file.path(file_path, paste0("Fig_C", plot_index, "_", prefix, "_", plot_name, "_pl_hist.png")))
    hist(bs[[i]]$pl$bootstraps[, 2], breaks = "fd", main = paste0("Fig. C", plot_index, " - ", ifelse(prefix == "chem", "ChemRxiv", "Control"), " - ", plot_name, " - Power Law Histogram"))
    dev.off()
    plot_index <- plot_index + 1
    
    # Log-Normal histogram
    png(filename = file.path(file_path, paste0("Fig_C", plot_index, "_", prefix, "_", plot_name, "_ln_hist.png")))
    hist(bs[[i]]$ln$bootstraps[, 2], breaks = "fd", main = paste0("Fig. C", plot_index, " - ", ifelse(prefix == "chem", "ChemRxiv", "Control"), " - ", plot_name, " - Log-Normal Histogram"))
    dev.off()
    plot_index <- plot_index + 1
    
    # Exponential histogram
    png(filename = file.path(file_path, paste0("Fig_C", plot_index, "_", prefix, "_", plot_name, "_exp_hist.png")))
    hist(bs[[i]]$exp$bootstraps[, 2], breaks = "fd", main = paste0("Fig. C", plot_index, " - ", ifelse(prefix == "chem", "ChemRxiv", "Control"), " - ", plot_name, " - Exponential Histogram"))
    dev.off()
    plot_index <- plot_index + 1
  })
}

# Plotting Function Call for Appendix C
plot_histograms_and_save_C(bs_chem, "chem", 1)
plot_histograms_and_save_C(bs_comp, "comp", 10)


# Function to add title space and save plot for Appendix B
add_title_and_save <- function(filename, plot_expr, title_text) {
  # Create a new PNG file with extra space for the title
  temp_filename <- paste0("temp_", filename)
  png(filename = temp_filename, width = 1600, height = 1155, res = 200)  # Height adjusted for extra space
  plot_expr
  dev.off()
  
  # Read the generated plot
  plot_img <- readPNG(temp_filename)
  
  # Create a new PNG with extra space for the title
  final_filename <- file.path(file_path, filename)
  png(filename = final_filename, width = 1600, height = 1200, res = 200)
  par(mar = c(0, 0, 0, 0))  # Remove margins
  plot.new()
  rasterImage(plot_img, 0, 0, 1, 0.925)  # Adjust the height to fit the title
  
  # Add title
  title(main = title_text, line = -2, outer = TRUE)
  dev.off()
  
  # Remove temporary file
  file.remove(temp_filename)
}

# Updated plot_bootstraps_and_save_B function to use the new method
plot_bootstraps_and_save_B <- function(bs_chem, bs_comp, plot_index_start) {
  plot_index <- plot_index_start  # Initialize the plot index
  
  for (i in seq_along(variables)) {
    var_name <- variables[i]
    plot_name <- variable_names[[var_name]]
    
    # ChemRxiv Power Law bootstrap plot
    add_title_and_save(
      paste0("Fig_B", plot_index, "_chem_", plot_name, "_pl_bootstrap.png"),
      plot(bs_chem[[i]]$pl, main = ""),
      paste0("Fig. B", plot_index, " - ChemRxiv - ", plot_name, " - Power Law Bootstrap")
    )
    plot_index <- plot_index + 1
    
    # ChemRxiv Log-Normal bootstrap plot
    add_title_and_save(
      paste0("Fig_B", plot_index, "_chem_", plot_name, "_ln_bootstrap.png"),
      plot(bs_chem[[i]]$ln, main = ""),
      paste0("Fig. B", plot_index, " - ChemRxiv - ", plot_name, " - Log-Normal Bootstrap")
    )
    plot_index <- plot_index + 1
    
    # ChemRxiv Exponential bootstrap plot
    add_title_and_save(
      paste0("Fig_B", plot_index, "_chem_", plot_name, "_exp_bootstrap.png"),
      plot(bs_chem[[i]]$exp, main = ""),
      paste0("Fig. B", plot_index, " - ChemRxiv - ", plot_name, " - Exponential Bootstrap")
    )
    plot_index <- plot_index + 1
    
    # Control Power Law bootstrap plot
    add_title_and_save(
      paste0("Fig_B", plot_index, "_comp_", plot_name, "_pl_bootstrap.png"),
      plot(bs_comp[[i]]$pl, main = ""),
      paste0("Fig. B", plot_index, " - Control - ", plot_name, " - Power Law Bootstrap")
    )
    plot_index <- plot_index + 1
    
    # Control Log-Normal bootstrap plot
    add_title_and_save(
      paste0("Fig_B", plot_index, "_comp_", plot_name, "_ln_bootstrap.png"),
      plot(bs_comp[[i]]$ln, main = ""),
      paste0("Fig. B", plot_index, " - Control - ", plot_name, " - Log-Normal Bootstrap")
    )
    plot_index <- plot_index + 1
    
    # Control Exponential bootstrap plot
    add_title_and_save(
      paste0("Fig_B", plot_index, "_comp_", plot_name, "_exp_bootstrap.png"),
      plot(bs_comp[[i]]$exp, main = ""),
      paste0("Fig. B", plot_index, " - Control - ", plot_name, " - Exponential Bootstrap")
    )
    plot_index <- plot_index + 1
  }
  
  return(plot_index)
}

# Plotting Function Call for Appendix B with updated method
plot_index_B <- 1

# Grouped by metrics
plot_index_B <- plot_bootstraps_and_save_B(bs_chem, bs_comp, plot_index_B)
