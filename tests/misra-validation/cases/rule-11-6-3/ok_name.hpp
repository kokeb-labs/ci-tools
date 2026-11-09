// Near miss: an implicit value equal to an explicit one that is just the name of another enumerator.
#ifndef KV_RULE_11_6_3_OK_NAME_HPP
#define KV_RULE_11_6_3_OK_NAME_HPP

#include <cstdint>

namespace kv::rule_11_6_3::ok_name {

enum class Reg : std::uint8_t { kA = 3, kB, kC, kLast = kC };

[[nodiscard]] inline bool last(Reg r) { return r == Reg::kLast; }

}  // namespace kv::rule_11_6_3::ok_name

#endif  // KV_RULE_11_6_3_OK_NAME_HPP
