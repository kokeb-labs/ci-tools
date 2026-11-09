// Compliant: no deprecated language or library feature.
#ifndef KV_RULE_4_1_2_NEGATE_ADAPTOR_OK_HPP
#define KV_RULE_4_1_2_NEGATE_ADAPTOR_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_2_negate_adaptor::ok {

class Value {
 public:
  explicit Value(std::uint32_t v) : v_(v) {}
  [[nodiscard]] std::uint32_t get() const { return v_; }

 private:
  std::uint32_t v_;
};

[[nodiscard]] inline std::uint32_t read(const Value& x) { return x.get(); }

}  // namespace kv::rule_4_1_2_negate_adaptor::ok

#endif  // KV_RULE_4_1_2_NEGATE_ADAPTOR_OK_HPP
