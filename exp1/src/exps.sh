
dvc exp run  -S train.train_data="timesData" -S train.n_est=100 -S featurize.max_features=12 -S featurize.world_rank=50 -S featurize.max_rank=100 -n timesData 
dvc exp run  -S train.train_data="shanghaiData" -S train.n_est=100 -S featurize.max_features=12 -S featurize.world_rank=50 -S featurize.max_rank=100 -n shanghaiData


dvc exp run  -S train.train_data="timesData" -S featurize.max_features=3 -S train.n_est=100 -S featurize.world_rank=50 -S featurize.max_rank=100 -n Tf3
dvc exp run  -S train.train_data="shanghaiData" -S featurize.max_features=3 -S train.n_est=100 -S featurize.world_rank=50 -S featurize.max_rank=100 -n Sf3
dvc exp run -S train.train_data="cwurData" -S featurize.max_features=3 -S train.n_est=100 -S featurize.world_rank=50 -S featurize.max_rank=100 -n Cf3

dvc exp run -S train.train_data="cwurData" -S featurize.max_rank=300 -S featurize.world_rank=150 -S featurize.max_features=12 -S train.n_est=100 -n Cmr300
dvc exp run -S train.train_data="timesData" -S featurize.max_features=12 -S featurize.max_rank=300 -S featurize.world_rank=150 -S train.n_est=100 -n Tmr300
dvc exp run  -S train.train_data="shanghaiData" -S featurize.max_rank=300 -S featurize.world_rank=150 -S featurize.max_features=12 -S train.n_est=100 -n Smr300

dvc exp run  -S train.train_data="timesData" -S train.n_est=64 -S featurize.max_rank=100 -S featurize.world_rank=50 -S featurize.max_features=12 -n Tnest64
dvc exp run  -S train.train_data="shanghaiData" -S train.n_est=64 -S featurize.max_rank=100 -S featurize.world_rank=50 -S featurize.max_features=12 -n Snest64
dvc exp run  -S train.train_data="cwurData" -S train.n_est=64 -S featurize.max_rank=100 -S featurize.world_rank=50 -S featurize.max_features=12 -n Cnest64


