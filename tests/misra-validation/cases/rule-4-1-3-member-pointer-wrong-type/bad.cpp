// Seeded violation: a pointer to a derived member applied to an object that is only a base.
#include <cstdint>

namespace kv::rule_4_1_3_member_pointer_wrong_type::bad {

struct Base {
  virtual ~Base() = default;
};
struct Derived : Base {
  std::uint32_t extra{0U};
};

std::uint32_t peek(Base* b) {
  std::uint32_t Base::*pm = static_cast<std::uint32_t Base::*>(&Derived::extra);
  return b->*pm;  // the object is a Base: it has no extra  // seeded
}

std::uint32_t run() {
  Base* b = new Base;
  const std::uint32_t v = peek(b);
  delete b;
  return v;
}

}  // namespace kv::rule_4_1_3_member_pointer_wrong_type::bad
