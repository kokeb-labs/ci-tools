// Compliant: members are reached by name; no offset is computed.
#ifndef KV_RULE_21_2_4_OK_HPP
#define KV_RULE_21_2_4_OK_HPP

#include <cstdint>

namespace kv::rule_21_2_4::ok {

struct Frame {
  std::uint8_t command;
  std::uint32_t payload;
};

[[nodiscard]] inline std::uint8_t command_of(const Frame& frame) { return frame.command; }

[[nodiscard]] inline std::uint32_t payload_of(const Frame& frame) { return frame.payload; }

}  // namespace kv::rule_21_2_4::ok

#endif  // KV_RULE_21_2_4_OK_HPP
