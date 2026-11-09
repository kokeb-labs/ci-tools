// Near misses (near): nullptr comparisons, and comparisons of non-virtual member pointers.
#ifndef KV_RULE_13_3_4_OK_NEAR_HPP
#define KV_RULE_13_3_4_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_13_3_4::ok_near {

class Meter {
 public:
  std::uint32_t low() const { return 0U; }
  std::uint32_t high() const { return 1U; }
};

using Read = std::uint32_t (Meter::*)() const;

inline bool unset(Read r) { return r == nullptr; }

inline bool is_low(Read r) { return r == &Meter::low; }

}  // namespace kv::rule_13_3_4::ok_near

#endif  // KV_RULE_13_3_4_OK_NEAR_HPP
