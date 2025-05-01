#!/bin/bash
#SBATCH -A 
#SBATCH -p                  
#SBATCH --gres=gpu:v100:4
#SBATCH -N 4                             
#SBATCH --cpus-per-task=8                
#SBATCH --mem=375G                       
#SBATCH --ntasks-per-node=1               
#SBATCH --time=72:00:00                   
#SBATCH --job-name=edm2_training          
#SBATCH --output=job_output_%j.log
#SBATCH --error=job_error_%j.log

module load anaconda
conda activate edm2

# Navigate to the directory containing your script

# Calculate total_nimg
number_of_epochs=100
n_samples=127488  
batch_size=1280
total_nimg=$((number_of_epochs * n_samples))


# Set master address and port for distributed training
MASTER_ADDR=$(scontrol show hostname $SLURM_NODELIST | head -n 1)
MASTER_PORT=29502  # Choose an available port

export MASTER_ADDR
export MASTER_PORT
export WORLD_SIZE=$((SLURM_NNODES * 4)) # nodes * gpus per node

nodes=( $( scontrol show hostnames $SLURM_JOB_NODELIST ) )
nodes_array=($nodes)
head_node=${nodes_array[0]}
head_node_ip=$(srun --nodes=1 --ntasks=1 -w "$head_node" hostname --ip-address)

# Set status, snapshot, and checkpoint intervals
status_nimg=$((batch_size * 10))     
snapshot_nimg=$((n_samples * 10))          # e.g., save snapshot #must be a multiple of both 1024 and batch size
checkpoint_nimg=$snapshot_nimg       

echo "MASTER_ADDR=$MASTER_ADDR"
echo "MASTER_PORT=$MASTER_PORT"
echo "WORLD_SIZE=$WORLD_SIZE"
echo "Rendezvous Endpoint: ${head_node_ip}:29502"

echo Node IP: ${head_node_ip}
export LOGLEVEL=INFO

for node in "${nodes_array[@]}"; do
    echo "Testing connectivity to $node"
    ping -c 4 "$node"
done

srun torchrun \
    --nnodes $SLURM_NNODES \
    --rdzv_id $RANDOM \
    --rdzv_backend=c10d \
    --rdzv_endpoint=${head_node_ip}:29502 \
    --nproc_per_node=4 \
    /edm2_fork/train_edm2.py \
    --outdir=/edm2_diffusion/training-runs/00001-edm2-img64-s \
    --data=/Angiogenesis_Generative_data/edm2_shuffled_images.zip \
    --preset=edm2-img64-s \
    --batch-gpu=4 \
    --batch=$batch_size \
    --duration=$total_nimg \
    --status=$status_nimg \
    --snapshot=$snapshot_nimg \
    --checkpoint=$checkpoint_nimg \
    --cond=True
