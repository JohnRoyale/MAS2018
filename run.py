from model import ShipModel
# run the model
model = ShipModel(4)
for i in range(100):
    print("-------------------------")
    print("Step:", i)
    model.step()

