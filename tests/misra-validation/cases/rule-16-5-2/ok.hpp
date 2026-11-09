#ifndef KV_RULE_16_5_2_OK_HPP
#define KV_RULE_16_5_2_OK_HPP

// Compliant: a named accessor instead of overloading unary &.
#include <cstdint>

namespace kv::rule_16_5_2::ok {

class Register {
 public:
  [[nodiscard]] std::uint32_t* storage() & { return &value_; }

 private:
  std::uint32_t value_ = 0U;
};

}  // namespace kv::rule_16_5_2::ok

#endif  // KV_RULE_16_5_2_OK_HPP
