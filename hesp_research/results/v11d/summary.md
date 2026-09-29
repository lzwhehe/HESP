# v1.1 part D (LLM-free)

| Group | Family | Config | Variant | N | Verified | Correct, unverified | Wrong | Escalated | Missed attack (n) | Cost |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D1 | sec | catalogue_confirm | all | 72 | 0.903 | 0.000 | 0.000 | 0.097 | 0 | 4.93 |
| D1 | sec | catalogue_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 4.00 |
| D1 | sec | catalogue_confirm | drift | 24 | 0.875 | 0.000 | 0.000 | 0.125 | 0 | 5.88 |
| D1 | sec | catalogue_confirm | noise | 24 | 0.833 | 0.000 | 0.000 | 0.167 | 0 | 4.92 |
| D1 | sec | eig_confirm | all | 72 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.54 |
| D1 | sec | eig_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D1 | sec | eig_confirm | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D1 | sec | eig_confirm | noise | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.88 |
| D1 | sec | eig_posterior | all | 72 | 0.917 | 0.083 | 0.000 | 0.000 | 0 | 2.35 |
| D1 | sec | eig_posterior | base | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.12 |
| D1 | sec | eig_posterior | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D1 | sec | eig_posterior | noise | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.54 |
| D1 | sec | static_confirm | all | 72 | 0.917 | 0.000 | 0.000 | 0.083 | 0 | 2.90 |
| D1 | sec | static_confirm | base | 24 | 0.875 | 0.000 | 0.000 | 0.125 | 0 | 3.00 |
| D1 | sec | static_confirm | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D1 | sec | static_confirm | noise | 24 | 0.875 | 0.000 | 0.000 | 0.125 | 0 | 3.33 |
| D1 | sigma | catalogue_confirm | all | 152 | 0.993 | 0.000 | 0.000 | 0.007 | 0 | 2.96 |
| D1 | sigma | catalogue_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.61 |
| D1 | sigma | catalogue_confirm | noise | 76 | 0.987 | 0.000 | 0.000 | 0.013 | 0 | 3.32 |
| D1 | sigma | eig_confirm | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.20 |
| D1 | sigma | eig_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.00 |
| D1 | sigma | eig_confirm | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.39 |
| D1 | sigma | eig_posterior | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.20 |
| D1 | sigma | eig_posterior | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.00 |
| D1 | sigma | eig_posterior | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.39 |
| D1 | sigma | static_confirm | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.20 |
| D1 | sigma | static_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.00 |
| D1 | sigma | static_confirm | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.39 |
| D2@0.6 | sec | eig_confirm | all | 72 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.54 |
| D2@0.6 | sec | eig_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.6 | sec | eig_confirm | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.6 | sec | eig_confirm | noise | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.88 |
| D2@0.6 | sec | eig_posterior | all | 72 | 0.917 | 0.083 | 0.000 | 0.000 | 0 | 2.35 |
| D2@0.6 | sec | eig_posterior | base | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.12 |
| D2@0.6 | sec | eig_posterior | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.6 | sec | eig_posterior | noise | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.54 |
| D2@0.6 | sigma | eig_confirm | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.12 |
| D2@0.6 | sigma | eig_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.00 |
| D2@0.6 | sigma | eig_confirm | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.25 |
| D2@0.6 | sigma | eig_posterior | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.12 |
| D2@0.6 | sigma | eig_posterior | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.00 |
| D2@0.6 | sigma | eig_posterior | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.25 |
| D2@0.7 | sec | eig_confirm | all | 72 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.54 |
| D2@0.7 | sec | eig_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.7 | sec | eig_confirm | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.7 | sec | eig_confirm | noise | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.88 |
| D2@0.7 | sec | eig_posterior | all | 72 | 0.917 | 0.083 | 0.000 | 0.000 | 0 | 2.35 |
| D2@0.7 | sec | eig_posterior | base | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.12 |
| D2@0.7 | sec | eig_posterior | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.7 | sec | eig_posterior | noise | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.54 |
| D2@0.7 | sigma | eig_confirm | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.12 |
| D2@0.7 | sigma | eig_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.00 |
| D2@0.7 | sigma | eig_confirm | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.25 |
| D2@0.7 | sigma | eig_posterior | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.12 |
| D2@0.7 | sigma | eig_posterior | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.00 |
| D2@0.7 | sigma | eig_posterior | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 1.25 |
| D2@0.8 | sec | eig_confirm | all | 72 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.54 |
| D2@0.8 | sec | eig_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.8 | sec | eig_confirm | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.8 | sec | eig_confirm | noise | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.88 |
| D2@0.8 | sec | eig_posterior | all | 72 | 0.917 | 0.083 | 0.000 | 0.000 | 0 | 2.35 |
| D2@0.8 | sec | eig_posterior | base | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.12 |
| D2@0.8 | sec | eig_posterior | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.38 |
| D2@0.8 | sec | eig_posterior | noise | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.54 |
| D2@0.8 | sigma | eig_confirm | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.20 |
| D2@0.8 | sigma | eig_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.00 |
| D2@0.8 | sigma | eig_confirm | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.39 |
| D2@0.8 | sigma | eig_posterior | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.20 |
| D2@0.8 | sigma | eig_posterior | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.00 |
| D2@0.8 | sigma | eig_posterior | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.39 |
| D2@0.95 | sec | eig_confirm | all | 72 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 4.14 |
| D2@0.95 | sec | eig_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.25 |
| D2@0.95 | sec | eig_confirm | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 5.25 |
| D2@0.95 | sec | eig_confirm | noise | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.92 |
| D2@0.95 | sec | eig_posterior | all | 72 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 3.86 |
| D2@0.95 | sec | eig_posterior | base | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 3.00 |
| D2@0.95 | sec | eig_posterior | drift | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 5.00 |
| D2@0.95 | sec | eig_posterior | noise | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 3.58 |
| D2@0.95 | sigma | eig_confirm | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.29 |
| D2@0.95 | sigma | eig_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.00 |
| D2@0.95 | sigma | eig_confirm | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.58 |
| D2@0.95 | sigma | eig_posterior | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.29 |
| D2@0.95 | sigma | eig_posterior | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.00 |
| D2@0.95 | sigma | eig_posterior | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.58 |
| D2@0.99 | sec | eig_confirm | all | 72 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 6.60 |
| D2@0.99 | sec | eig_confirm | base | 24 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 5.62 |
| D2@0.99 | sec | eig_confirm | drift | 24 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 7.62 |
| D2@0.99 | sec | eig_confirm | noise | 24 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 6.54 |
| D2@0.99 | sec | eig_posterior | all | 72 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 6.60 |
| D2@0.99 | sec | eig_posterior | base | 24 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 5.62 |
| D2@0.99 | sec | eig_posterior | drift | 24 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 7.62 |
| D2@0.99 | sec | eig_posterior | noise | 24 | 0.500 | 0.500 | 0.000 | 0.000 | 0 | 6.54 |
| D2@0.99 | sigma | eig_confirm | all | 152 | 0.914 | 0.079 | 0.000 | 0.007 | 0 | 4.39 |
| D2@0.99 | sigma | eig_confirm | base | 76 | 0.921 | 0.079 | 0.000 | 0.000 | 0 | 4.00 |
| D2@0.99 | sigma | eig_confirm | noise | 76 | 0.908 | 0.079 | 0.000 | 0.013 | 0 | 4.79 |
| D2@0.99 | sigma | eig_posterior | all | 152 | 0.914 | 0.079 | 0.000 | 0.007 | 0 | 4.39 |
| D2@0.99 | sigma | eig_posterior | base | 76 | 0.921 | 0.079 | 0.000 | 0.000 | 0 | 4.00 |
| D2@0.99 | sigma | eig_posterior | noise | 76 | 0.908 | 0.079 | 0.000 | 0.013 | 0 | 4.79 |
| D2@0.9 | sec | eig_confirm | all | 72 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.75 |
| D2@0.9 | sec | eig_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.88 |
| D2@0.9 | sec | eig_confirm | drift | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 4.88 |
| D2@0.9 | sec | eig_confirm | noise | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.50 |
| D2@0.9 | sec | eig_posterior | all | 72 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 3.47 |
| D2@0.9 | sec | eig_posterior | base | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.62 |
| D2@0.9 | sec | eig_posterior | drift | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 4.62 |
| D2@0.9 | sec | eig_posterior | noise | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 3.17 |
| D2@0.9 | sigma | eig_confirm | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.20 |
| D2@0.9 | sigma | eig_confirm | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.00 |
| D2@0.9 | sigma | eig_confirm | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.39 |
| D2@0.9 | sigma | eig_posterior | all | 152 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.20 |
| D2@0.9 | sigma | eig_posterior | base | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.00 |
| D2@0.9 | sigma | eig_posterior | noise | 76 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.39 |
| D3 absent | sec | eig_confirm | all | 48 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 4.81 |
| D3 absent | sec | eig_confirm | base | 24 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 4.75 |
| D3 absent | sec | eig_confirm | noise | 24 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 4.88 |
| D3 absent | sec | eig_posterior | all | 48 | 0.000 | 0.000 | 0.500 | 0.500 | 0 | 2.17 |
| D3 absent | sec | eig_posterior | base | 24 | 0.000 | 0.000 | 0.500 | 0.500 | 0 | 2.00 |
| D3 absent | sec | eig_posterior | noise | 24 | 0.000 | 0.000 | 0.500 | 0.500 | 0 | 2.33 |
| D3 confusion 0.25 | sec | eig_confirm | all | 48 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 10.00 |
| D3 confusion 0.25 | sec | eig_confirm | base | 24 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 10.00 |
| D3 confusion 0.25 | sec | eig_confirm | noise | 24 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 10.00 |
| D3 confusion 0.25 | sec | eig_posterior | all | 48 | 0.979 | 0.000 | 0.000 | 0.021 | 0 | 3.90 |
| D3 confusion 0.25 | sec | eig_posterior | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 3.62 |
| D3 confusion 0.25 | sec | eig_posterior | noise | 24 | 0.958 | 0.000 | 0.000 | 0.042 | 0 | 4.17 |
| D3 confusion 0.5 | sec | eig_confirm | all | 48 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 10.00 |
| D3 confusion 0.5 | sec | eig_confirm | base | 24 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 10.00 |
| D3 confusion 0.5 | sec | eig_confirm | noise | 24 | 0.000 | 0.000 | 0.000 | 1.000 | 0 | 10.00 |
| D3 confusion 0.5 | sec | eig_posterior | all | 48 | 0.125 | 0.000 | 0.000 | 0.875 | 0 | 9.42 |
| D3 confusion 0.5 | sec | eig_posterior | base | 24 | 0.125 | 0.000 | 0.000 | 0.875 | 0 | 9.38 |
| D3 confusion 0.5 | sec | eig_posterior | noise | 24 | 0.125 | 0.000 | 0.000 | 0.875 | 0 | 9.46 |
| D3 mirror | sec | eig_confirm | all | 48 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.73 |
| D3 mirror | sec | eig_confirm | base | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.50 |
| D3 mirror | sec | eig_confirm | noise | 24 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 2.96 |
| D3 mirror | sec | eig_posterior | all | 48 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.33 |
| D3 mirror | sec | eig_posterior | base | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.12 |
| D3 mirror | sec | eig_posterior | noise | 24 | 0.875 | 0.125 | 0.000 | 0.000 | 0 | 2.54 |
