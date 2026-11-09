// Seeded violation: a member operator&&.
namespace kv::rule_16_5_1::bad_member {

struct Gate {
  bool open = false;
  bool operator&&(const Gate& other) const { return open && other.open; }
};

}  // namespace kv::rule_16_5_1::bad_member
