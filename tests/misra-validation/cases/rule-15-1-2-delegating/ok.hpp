// Near miss: a delegating constructor; the target names the base.
#ifndef KV_RULE_15_1_2_OK_DELEGATE_HPP
#define KV_RULE_15_1_2_OK_DELEGATE_HPP

#include <cstdint>

namespace kv::rule_15_1_2_delegating::ok_delegate {

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
  Derived() : Derived(1U) {}

  [[nodiscard]] std::uint32_t width() const { return width_; }

 private:
  std::uint32_t width_;
};

}  // namespace kv::rule_15_1_2_delegating::ok_delegate

#endif  // KV_RULE_15_1_2_OK_DELEGATE_HPP
