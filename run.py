from model import ShipModel
# run the model
model = ShipModel(4)

n_worlds = len(model.kripke_model.ks.worlds)

i = 0
while model.running:
    print("-------------------------")
    print("Step:", i)
    model.step()
    i += 1


print(n_worlds)






