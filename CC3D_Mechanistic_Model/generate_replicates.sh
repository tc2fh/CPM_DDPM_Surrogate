#!/bin/bash
#SBATCH --account=
#SBATCH --partition=standard

# Define the base output directory
base_output_dir=""
output_log_dir="$base_output_dir/logs"
workspace_dump_dir="$base_output_dir/cc3d_workspace_dump"


# Create the output directories if they don't exist
mkdir -p "$base_output_dir"
mkdir -p "$output_log_dir"
mkdir -p "$workspace_dump_dir"

# Define the parameter space and number of replicates
sim_rep_numbers=( $(seq 0 1 9) )
contact_param_array=(0 5 10 15 20) #contact_param = np.linspace(0,20,5)
decay_param_array=(0.05 0.1875 0.325 0.4625 0.6) #decay_param = np.linspace(0.05,.6,5)


for contact_param in "${contact_param_array[@]}"; do
    for decay_param in "${decay_param_array[@]}"; do

        # Create a directory for this combination of parameters
        contact_decay_dir="$base_output_dir/contact_${contact_param}_decay_${decay_param}"
        mkdir -p "$contact_decay_dir"

        for rep_number in "${sim_rep_numbers[@]}"; do
            # Submit a job for this combination of parameters
            sbatch \
                --account=bii_dsc_community \
                --partition=standard \
                --job-name="angiogenesis_generative_data_contact_${contact_param}_decay_${decay_param}_rep${rep_number}" \
                --output="$output_log_dir/result_rep_${rep_number}_contact_${contact_param}_decay_${decay_param}.out" \
                --nodes=1 \
                --ntasks-per-node=1 \
                --mem-per-cpu=5G \
                --time=01:00:00 \
                --wrap="module load anaconda; \
                                conda activate cc3d_450; \
                                chmod +x generate_replicates.py; \
                                python generate_replicates.py $contact_param $decay_param $rep_number $contact_decay_dir $workspace_dump_dir"
        done
    done
done
