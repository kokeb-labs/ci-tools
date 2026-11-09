// Seeded violation (enum): a bit-field of an unscoped enumeration with no fixed underlying type.
namespace kv::rule_12_2_2::bad_enum {

enum Direction { kTop, kLeft, kBottom, kRight };

struct Cursor {
  Direction dir : 4;  // seeded
};

bool at_top(const Cursor& c) { return c.dir == kTop; }

}  // namespace kv::rule_12_2_2::bad_enum
