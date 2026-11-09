// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_4_1_OK_NEAR_HPP
#define KV_RULE_6_4_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_4_1::near {

// The same name in sibling scopes hides nothing.
inline std::uint32_t loops(std::uint32_t n) {
  std::uint32_t acc = 0U;
  for (std::uint32_t i = 0U; i < n; ++i) {
    acc |= i;
  }
  for (std::uint32_t i = 0U; i < n; ++i) {
    acc ^= i;
  }
  return acc;
}
class Gauge {
 public:
  explicit Gauge(std::int32_t start) : level_(start) {}
  [[nodiscard]] std::int32_t read() const { return level_; }

 private:
  std::int32_t level_;
};

}  // namespace kv::rule_6_4_1::near

#endif  // KV_RULE_6_4_1_OK_NEAR_HPP
