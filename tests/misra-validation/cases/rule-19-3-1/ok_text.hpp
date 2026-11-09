// Near miss: # and ## inside a string literal are just characters.
#ifndef KV_RULE_19_3_1_OK_TEXT_HPP
#define KV_RULE_19_3_1_OK_TEXT_HPP

namespace kv::rule_19_3_1::ok_text {

constexpr const char* kHelp = "use # for a channel, ## for a bank";

[[nodiscard]] inline bool has_help() { return kHelp != nullptr; }

}  // namespace kv::rule_19_3_1::ok_text

#endif  // KV_RULE_19_3_1_OK_TEXT_HPP
