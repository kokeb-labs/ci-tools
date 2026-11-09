// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_0_4_OK_NEAR_HPP
#define KV_RULE_6_0_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_0_4::near {

// Names that contain main but are not main.
inline std::int32_t main_loop() { return 0; }
struct App {
  [[nodiscard]] std::int32_t run_main() const { return main_loop(); }
};

}  // namespace kv::rule_6_0_4::near

#endif  // KV_RULE_6_0_4_OK_NEAR_HPP
