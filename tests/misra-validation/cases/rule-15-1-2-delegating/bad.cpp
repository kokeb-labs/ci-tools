// Seeded violation: the constructor leaves its base class out of the initializer list.
#include <cstdint>

namespace kv::rule_15_1_2_delegating::bad {

class Base {
 public:
  explicit Base(std::uint32_t v) : value_(v) {}
  Base() = default;

 private:
  std::uint32_t value_ = 0U;
};

class Derived : public Base {
 public:
  explicit Derived(std::uint32_t w) : width_(w) {}  // seeded

 private:
  std::uint32_t width_;
};

}  // namespace kv::rule_15_1_2_delegating::bad
