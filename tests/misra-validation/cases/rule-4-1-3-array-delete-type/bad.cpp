// Seeded violation: an array of derived objects deleted through a base pointer.
#include <cstdint>

namespace kv::rule_4_1_3_array_delete_type::bad {

struct Base {
  virtual ~Base() = default;
  std::uint32_t a{0U};
};
struct Derived : Base {
  std::uint32_t b{0U};
};

void release() {
  Base* items = new Derived[2];
  delete[] items;  // array of Derived deleted through Base*  // seeded
}

}  // namespace kv::rule_4_1_3_array_delete_type::bad
