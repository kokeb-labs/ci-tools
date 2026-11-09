// Seeded violation: a copy constructor that does not initialise its base explicitly.
#include <cstdint>

namespace kv::rule_15_1_2::bad_copy {

class Base {
 public:
  Base() = default;
  Base(const Base&) = default;

 private:
  std::uint32_t value_ = 0U;
};

class Derived : public Base {
 public:
  Derived() = default;
  Derived(const Derived& other) : width_(other.width_) {}

 private:
  std::uint32_t width_ = 0U;
};

}  // namespace kv::rule_15_1_2::bad_copy
