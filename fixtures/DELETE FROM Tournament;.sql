DELETE FROM Tournament;
DELETE FROM Players;
DELETE FROM Players_Tournament;

SELECT * FROM Tournament t
LEFT JOIN Players_Tournament pt ON t.id = pt.tournament
WHERE pt.tournament IS NULL