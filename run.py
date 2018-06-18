from model import ShipModel
# run the model
model = ShipModel(4)

n_worlds = len(model.kripke_model.ks.worlds)

for i in range(1000):
    print("-------------------------")
    print("Step:", i)
    model.step()
    input()

print(n_worlds)