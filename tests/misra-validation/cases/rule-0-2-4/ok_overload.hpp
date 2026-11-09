// Near miss: an uncalled private overload is used when another function of its overload set is called.
#ifndef KV_RULE_0_2_4_OK_OVERLOAD_HPP
#define KV_RULE_0_2_4_OK_OVERLOAD_HPP

#include <cstdint>

namespace kv::rule_0_2_4::ok_overload {

class Scaler {
 public:
  [[nodiscard]] std::uint32_t scaled(std::uint32_t v) const { return scale(v); }

 private:
  [[nodiscard]] static std::uint32_t scale(std::uint32_t v) { return v << 1U; }
  [[nodiscard]] static std::uint64_t scale(std::uint64_t v) { return v << 2U; }
};

}  // namespace kv::rule_0_2_4::ok_overload

#endif  // KV_RULE_0_2_4_OK_OVERLOAD_HPP
