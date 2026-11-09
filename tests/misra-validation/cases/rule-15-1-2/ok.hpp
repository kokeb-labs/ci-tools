#ifndef KV_RULE_15_1_2_OK_HPP
#define KV_RULE_15_1_2_OK_HPP

// Compliant: the constructor names its base in the initializer list.
#include <cstdint>

namespace kv::rule_15_1_2::ok {

class Base {
 public:
  explicit Base(std::uint32_t v) : value_(v) {}

  [[nodiscard]] std::uint32_t value() const { return value_; }

 private:
  std::uint32_t value_;
};

class Derived : public Base {
 public:
  explicit Derived(std::uint32_t w) : Base(w), width_(w) {}

  [[nodiscard]] std::uint32_t width() const { return width_; }

 private:
  std::uint32_t width_;
};

}  // namespace kv::rule_15_1_2::ok

#endif  // KV_RULE_15_1_2_OK_HPP
