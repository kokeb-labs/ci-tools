// Seeded violation: a downcast from a virtual base without dynamic_cast.
namespace kv::rule_8_2_1::bad {

struct Node {
  virtual ~Node() = default;
  int id{0};
};

struct Leaf : virtual Node {  // seeded: clang-tidy
  int weight{0};
};

int weight_of(Node* node) {
  Leaf* leaf = reinterpret_cast<Leaf*>(node);  // seeded: codeql
  return leaf->weight;
}

}  // namespace kv::rule_8_2_1::bad
