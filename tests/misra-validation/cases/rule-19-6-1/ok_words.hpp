// Near miss: the word, not the directive.
#ifndef KV_RULE_19_6_1_OK_WORDS_HPP
#define KV_RULE_19_6_1_OK_WORDS_HPP

#include <cstdint>

namespace kv::rule_19_6_1::ok_words {

constexpr const char* kNote = "no #pragma once here";
constexpr std::uint8_t kPragmaticLimit = 4U;

}  // namespace kv::rule_19_6_1::ok_words

#endif  // KV_RULE_19_6_1_OK_WORDS_HPP
