// Seeded violation: a derived class declares a member that hides a non-virtual base member.
#include <cstdint>

namespace kv::rule_6_4_2_nonvirtual::bad {

class Base {
 public:
  std::int32_t level() const { return 1; }
};

class Derived : public Base {
 public:
  std::int32_t level(std::int32_t bias) const { return bias; }
};

std::int32_t use(Derived const& d) { return d.level(2); }

}  // namespace kv::rule_6_4_2_nonvirtual::bad
