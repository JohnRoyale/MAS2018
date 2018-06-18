from model import ShipModel
# run the model
model = ShipModel(5)

n_worlds = len(model.kripke_model.ks.worlds)

for i in range(100):
    print("-------------------------")
    print("Step:", i)
    model.step()

print(n_worlds)






