// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_2_4_OK_NEAR_HPP
#define KV_RULE_0_2_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_2_4::near {

class Timer {
 public:
  [[nodiscard]] std::uint32_t now() const {
    const auto f = [this]() { return scale(ticks_); };
    return f();
  }

 private:
  // Called only from the lambda inside now(): still a use.
  [[nodiscard]] static std::uint32_t scale(std::uint32_t v) { return v << 2U; }
  std::uint32_t ticks_{0U};
};

}  // namespace kv::rule_0_2_4::near

#endif  // KV_RULE_0_2_4_OK_NEAR_HPP
