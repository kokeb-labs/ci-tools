// Compliant: the bit-fields that exist use a fixed-width unsigned type (unsigned int) and bool.
#ifndef KV_RULE_12_2_2_OK_HPP
#define KV_RULE_12_2_2_OK_HPP

#include <cstdint>

namespace kv::rule_12_2_2::ok {

struct Packed {
  std::uint32_t level : 4;
  bool ready : 1;
};

inline std::uint32_t level_if_ready(const Packed& p) { return p.ready ? p.level : 0U; }

}  // namespace kv::rule_12_2_2::ok

#endif  // KV_RULE_12_2_2_OK_HPP
